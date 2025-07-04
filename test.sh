#!/usr/bin/env bash

set -eo pipefail
shopt -s lastpipe extglob

self="$(basename "$0")"
title="$self: Verify Pydantic Overture schema"
declare -A modes
declare -a patterns

function usage() {
  >&2 <<EOF cat
usage: $self [OPTIONS] [PATTERNS]
  (or: $self --help)
EOF
}

function help() {
  >&2 <<EOF cat
$title

OPTIONS:
  -m, --mode=MODE validation mode - schema|examples|counterexamples
                   this argument maybe specified more than once, e.g.
                   \`-m schema -m examples\`. if this argument is omitted,
                   all validation modes are run.
  -v, --verbose   show detailed information including theme:type detection

EXAMPLES:
  $self --help
  $self
  $self -m schema
  $self -m examples -m counterexamples "transportation/.*\.json$"
EOF
}

function emit() {
  >&2 printf '%s: %s\n' "$self" "$*"
}

function bad_usage() {
  emit "$*"
  usage
  exit 64
}

function parse_args() {
  while (($#)); do
    local arg="$1"
    shift

    case "$arg" in
      -m|--mode)
        add_mode "$1"
        shift
        ;;
      --mode=*)
        add_mode "${arg/#*=/}"
        ;;
      -v|--verbose)
        VERBOSE=1
        ;;
      -h|--help)
        usage
        echo
        help
        exit 0
        ;;
      *)
        patterns=("$arg" "$@")
        break
        ;;
    esac
  done

  if [ "${#modes[@]}" -eq 0 ]; then
    modes=([schema]=yes [examples]=yes [counterexamples]=yes)
  fi
}

function add_mode() {
  mode="$1"
  case "$mode" in
    s|sc|sch|sche|schem|schema)
      mode=schema
      ;;
    e|ex|exa|exam|examp|exampl|example|examples)
      mode=examples
      ;;
    c|co|cou|coun|count|counte|counter|countere|counterex|counterexa|counterexam|counterexamp|counterexampl|counterexample|counterexamples)
      mode=counterexamples
      ;;
    *)
      bad_usage "invalid mode: '$mode'. valid modes are: schema|examples|counterexamples"
      ;;
  esac
  modes["$mode"]=yes
}

# Default schema file (for backward compatibility)
schema_file=overture-schema.json

function extract_theme_type() {
  local instance_file="$1"
  local theme=""
  local type=""
  
  # Extract theme and type from file path
  # Examples:
  # reference/examples/addresses/address.yaml -> theme=addresses, type=address
  # reference/counterexamples/transportation/segment/bad-class.yaml -> theme=transportation, type=segment
  # reference/examples/buildings/building-polygon.yaml -> theme=buildings, type=building
  
  if [[ "$instance_file" =~ reference/(examples|counterexamples)/([^/]+)/([^/]+) ]]; then
    theme="${BASH_REMATCH[2]}"
    local path_component="${BASH_REMATCH[3]}"
    
    # Handle different path patterns
    case "$theme" in
      addresses)
        type="address"
        ;;
      base)
        # base/bathymetry-example.yaml -> type=bathymetry
        # base/infrastructure/infrastructure-example.yaml -> type=infrastructure
        if [[ "$instance_file" =~ reference/(examples|counterexamples)/base/([^/]+) ]]; then
          local base_component="${BASH_REMATCH[2]}"
          # Extract type from filename pattern
          if [[ "$base_component" =~ ^([^-]+) ]]; then
            type="${BASH_REMATCH[1]}"
          elif [[ "$instance_file" =~ reference/(examples|counterexamples)/base/([^/]+)/([^/]+) ]]; then
            # Handle subdirectory case: base/bathymetry/bad-depth.yaml
            type="${BASH_REMATCH[2]}"
          fi
        fi
        ;;
      buildings)
        # Most buildings are type=building, but building_part is separate
        if [[ "$instance_file" =~ building-part ]]; then
          type="building_part"
        else
          type="building"
        fi
        ;;
      divisions)
        # divisions/division/, divisions/division_area/, divisions/division_boundary/
        if [[ "$instance_file" =~ reference/(examples|counterexamples)/divisions/([^/]+) ]]; then
          type="${BASH_REMATCH[2]}"
        fi
        ;;
      places)
        type="place"
        ;;
      transportation)
        # transportation/segment/, transportation/connector/
        if [[ "$instance_file" =~ reference/(examples|counterexamples)/transportation/([^/]+) ]]; then
          type="${BASH_REMATCH[2]}"
        fi
        ;;
    esac
  fi
  
  # Output theme:type (or empty if not detected)
  if [[ -n "$theme" && -n "$type" ]]; then
    echo "${theme}:${type}"
  fi
}

function get_schema_file() {
  local instance_file="$1"
  local theme_type
  theme_type=$(extract_theme_type "$instance_file")
  
  if [[ -n "$theme_type" ]]; then
    local theme="${theme_type%:*}"
    local type="${theme_type#*:}"
    local specific_schema="overture-schema-${theme}-${type}.json"
    
    # Generate schema if it doesn't exist
    if [[ ! -f "$specific_schema" ]]; then
      >&2 printf "Generating schema for %s:%s...\n" "$theme" "$type"
      if ! uv run python -m packages.overture-schema.src.overture.schema --theme "$theme" --type "$type" > "$specific_schema" 2>/dev/null; then
        >&2 printf "Failed to generate schema for %s:%s, falling back to default\n" "$theme" "$type"
        echo "$schema_file"
        return
      fi
    fi
    
    echo "$specific_schema"
  else
    # Fall back to default schema
    echo "$schema_file"
  fi
}

function match() {
  if [ "${#patterns}" == 0 ]; then
    return 0
  else
    candidate="$1"
    for pattern in "${patterns[@]}"; do
      if [[ "$candidate" =~ $pattern ]]; then
        return 0
      fi
    done
    return 1
  fi
}

function verify() {
  local mode="$1"
  local instance_file="${2:-}"
  
  # Determine which schema file to use
  local current_schema_file="$schema_file"
  if [ -n "$instance_file" ]; then
    current_schema_file=$(get_schema_file "$instance_file")
  fi

  local -a jv_args=(--assert-format --assert-content "$current_schema_file")
  if [ -n "$instance_file" ]; then
    jv_args+=("$instance_file")
  fi

  case "$mode" in
  quiet)
    jv "${jv_args[@]}" >/dev/null 2>/dev/null
    ;;
  simple)
    jv --output alt "${jv_args[@]}"
    ;;
  *)
    jv --output "$mode" "${jv_args[@]}"
    ;;
  esac
}

function expected_errors() {
  local instance_file="$1"
  local type
  type=$(yq -r '.properties | type' "$instance_file")
  if [[ "$type" != "object" && "$type" != "!!map" ]]; then
    return 1
  fi
  yq -r '(.properties.ext_expected_errors // []) | .[]' "$instance_file"
}

function contains() {
  local haystack="$1"
  local needle="$2"
  grep -qF "$needle" <<<"$haystack"
}

function schema() {
  echo "---- VERIFYING schema ----"
  printf "%s..." "$schema_file"
  if verify quiet; then
    echo OK
  else
      echo FAILED
      printf "\nthe schema itself is invalid.\n"
      verify detailed
  fi
}

function examples() {
  echo "---- VERIFYING examples ----"
  find reference/examples -type f | sort | while read -r instance_file; do
    if ! [[ "$instance_file" == *.yaml ]] && ! [[ "$instance_file" == *.json ]]; then
      printf "%s...FAILED\nexample instance '%s' is EXPECTED to be a .yaml or .json file but ACTUALLY it is not.\n" "$instance_file" "$instance_file"
      continue
    elif ! match "$instance_file"; then
      continue
    fi
    
    # Show which schema is being used (in debug mode or if VERBOSE is set)
    local schema_info=""
    if [[ "${VERBOSE:-}" == "1" ]]; then
      local theme_type
      theme_type=$(extract_theme_type "$instance_file")
      if [[ -n "$theme_type" ]]; then
        schema_info=" [${theme_type}]"
      fi
    fi
    
    printf "%s%s..." "$instance_file" "$schema_info"
    if verify quiet "$instance_file"; then
      echo OK
    else
      echo FAILED
      printf "\nexample instance '%s' is EXPECTED to pass validation but ACTUALLY it failed.\n" "$instance_file"
      
      # Show which schema was used
      local used_schema
      used_schema=$(get_schema_file "$instance_file")
      printf "Schema used: %s\n" "$used_schema"
      
      verify detailed "$instance_file"
    fi
  done
}

function counterexamples() {
  echo "---- VERIFYING counterexamples ----"
  yq_installed=
  if command -v yq >/dev/null; then
    yq_installed=true
  else
    >&2 printf "WARNING: yq is not installed. Install yq for higher-fidelity counterexample testing.\n"
  fi
  find reference/counterexamples -type f | sort | while read -r instance_file; do
    if ! match "$instance_file"; then
      continue
    fi
    
    # Show which schema is being used (in debug mode or if VERBOSE is set)
    local schema_info=""
    if [[ "${VERBOSE:-}" == "1" ]]; then
      local theme_type
      theme_type=$(extract_theme_type "$instance_file")
      if [[ -n "$theme_type" ]]; then
        schema_info=" [${theme_type}]"
      fi
    fi
    
    printf "%s%s..." "$instance_file" "$schema_info"
    declare -a expected_errors
    if verify quiet "$instance_file"; then
      echo FAILED
      printf "\ncounterexample instance '%s' is EXPECTED to fail validation but ACTUALLY it passed.\n" "$instance_file"
      
      # Show which schema was used
      local used_schema
      used_schema=$(get_schema_file "$instance_file")
      printf "Schema used: %s\n" "$used_schema"
      
    elif [ -z "$yq_installed" ] || ! expected_errors "$instance_file" | mapfile -t expected_errors || [ ${#expected_errors} == 0 ]; then
      echo OK
    else
      declare -a actual_errors
      (verify simple "$instance_file" || true) 2>&1 | mapfile -t actual_errors
      for expected_error in "${expected_errors[@]}"; do
        for actual_error in "${actual_errors[@]}"; do
          if contains "$actual_error" "$expected_error"; then
            continue 2
          fi
        done
        echo FAILED
        printf "\ncounterexample instance '%s' is EXPECTED to trigger the following validation error but ACTUALLY it did not.\n\n" "$instance_file"
        printf "%s\n" "------------------------ MISSED EXPECTED ERROR -----------------------"
        printf "%s\n\n" "$expected_error"
        printf "%s\n" "---------------------- ACTUAL VALIDATION OUTPUT ----------------------"
        printf "%s\n" "${actual_errors[@]}"
        
        # Show which schema was used
        local used_schema
        used_schema=$(get_schema_file "$instance_file")
        printf "%s\n" "------------------------"
        printf "Schema used: %s\n" "$used_schema"
      done
      echo OK
    fi
  done
}

parse_args "$@"

need_newline=

function optional_newline() {
  if [ "$need_newline" == yes ]; then
    echo
    need_newline=no
  fi
}

if [ "${modes[schema]}" == yes ]; then
  schema
  need_newline=yes
fi

if [ "${modes[examples]}" == yes ]; then
  optional_newline
  examples
  need_newline=yes
fi

if [ "${modes[counterexamples]}" == yes ]; then
  optional_newline
  counterexamples
  need_newline=yes
fi