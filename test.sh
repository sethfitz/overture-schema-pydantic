#!/opt/homebrew/bin/bash
#!/usr/bin/env bash

set -eo pipefail
shopt -s lastpipe extglob

self="$(basename "$0")"
title="$self: Verify Pydantic Overture schema"
declare -A modes
declare -a patterns

# Color definitions
if [[ -t 2 ]]; then  # Only use colors if stderr is a terminal
  readonly RED='\033[0;31m'
  readonly GREEN='\033[0;32m'
  readonly YELLOW='\033[0;33m'
  readonly BLUE='\033[0;34m'
  readonly MAGENTA='\033[0;35m'
  readonly CYAN='\033[0;36m'
  readonly BOLD='\033[1m'
  readonly DIM='\033[2m'
  readonly RESET='\033[0m'
else
  readonly RED=''
  readonly GREEN=''
  readonly YELLOW=''
  readonly BLUE=''
  readonly MAGENTA=''
  readonly CYAN=''
  readonly BOLD=''
  readonly DIM=''
  readonly RESET=''
fi

# Capture process start time for schema regeneration checks
process_start_ref=$(mktemp)
# Create temporary directory for generated schemas
temp_schema_dir=$(mktemp -d)
trap "rm -f $process_start_ref; rm -rf $temp_schema_dir" EXIT

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

# Helper functions for colored output
function print_success() {
  printf "${GREEN}%s${RESET}\n" "$*"
}

function print_failure() {
  printf "${RED}%s${RESET}\n" "$*"
}

function print_warning() {
  printf "${YELLOW}%s${RESET}\n" "$*"
}

function print_info() {
  printf "${CYAN}%s${RESET}\n" "$*"
}

function print_section() {
  printf "\n${BOLD}${BLUE}%s${RESET}\n" "$*"
}

function print_status() {
  local status="$1"
  shift
  case "$status" in
    "OK"|"PASS")
      printf "%s...${GREEN}%s${RESET}\n" "$*" "$status"
      ;;
    "FAILED"|"FAIL")
      printf "%s...${RED}%s${RESET}\n" "$*" "$status"
      ;;
    "WARN"|"WARNING")
      printf "%s...${YELLOW}%s${RESET}\n" "$*" "$status"
      ;;
    *)
      printf "%s...%s\n" "$*" "$status"
      ;;
  esac
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

# Per-theme-type schema generation only - no monolithic schema support

function extract_theme_type() {
  local instance_file="$1"
  local theme=""
  local type=""

  # Extract theme and type from the YAML/JSON content using yq
  if command -v yq >/dev/null; then
    # Check if the file has properties.theme and properties.type
    if theme=$(yq -r '.properties.theme' "$instance_file" 2>/dev/null) && [[ -n "$theme" && "$theme" != "null" ]]; then
      if type=$(yq -r '.properties.type' "$instance_file" 2>/dev/null) && [[ -n "$type" && "$type" != "null" ]]; then
        echo "${theme}:${type}"
        return
      fi
    fi
  fi

  # Fallback: if yq is not available or extraction fails, return empty
  # This will cause the test to fail as we require theme/type extraction
}

function get_schema_file() {
  local instance_file="$1"
  local theme_type
  theme_type=$(extract_theme_type "$instance_file")

  if [[ -n "$theme_type" ]]; then
    local theme="${theme_type%:*}"
    local type="${theme_type#*:}"
    local specific_schema="$temp_schema_dir/overture-schema-${theme}-${type}.json"

    # Generate schema if it doesn't exist or if it's older than process start time
    if [[ ! -f "$specific_schema" ]] || [[ "$specific_schema" -ot "$process_start_ref" ]]; then
      if ! uv run python -m packages.overture-schema.src.overture.schema --theme "$theme" --type "$type" > "$specific_schema" 2>/dev/null; then
        exit 1
      fi
    fi

    echo "$specific_schema"
  else
    # Require theme/type extraction for all files
    exit 1
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
  local current_schema_file
  if [ -n "$instance_file" ]; then
    current_schema_file=$(get_schema_file "$instance_file")
  else
    >&2 printf "${RED}ERROR: Schema validation requires an instance file for theme/type extraction${RESET}\n"
    exit 1
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

function normalize_property_path() {
  local path="$1"
  # Remove leading slash and normalize property paths
  # Convert paths like "shapeContainer/properties/num_floors" to "num_floors"
  # Convert paths like "/properties/height" to "height"
  echo "$path" | sed -E 's|^/||' | sed -E 's|.*properties/([^/]+).*|\1|' | sed -E 's|.*/([^/]+)$|\1|'
}

function extract_constraint_info() {
  local error_msg="$1"
  # Extract the constraint type and values (e.g., "exclusiveMinimum: got -1.23, want 0")
  echo "$error_msg" | grep -oE '[a-zA-Z]+: got .+, want .+|[a-zA-Z]+: .+|value must be .+|missing propert(y|ies) .+|.*is not valid [a-zA-Z-]+.*'
}

function flexible_contains() {
  local haystack="$1"
  local needle="$2"

  # First try exact match
  if contains "$haystack" "$needle"; then
    return 0
  fi

  # Extract property name and constraint info from both
  local needle_property needle_constraint
  needle_property=$(normalize_property_path "$needle")
  needle_constraint=$(extract_constraint_info "$needle")

  local haystack_property haystack_constraint
  haystack_property=$(normalize_property_path "$haystack")
  haystack_constraint=$(extract_constraint_info "$haystack")

  # Check if property names match (or are related) and constraint info matches
  if [[ -n "$needle_constraint" && -n "$haystack_constraint" ]]; then
    # Match on constraint type and values, being more flexible about property paths
    if [[ "$needle_constraint" == "$haystack_constraint" ]]; then
      return 0
    fi
    # Also try matching just the constraint part (e.g., "exclusiveMinimum: got -1.23, want 0")
    if grep -qF "$needle_constraint" <<<"$haystack_constraint"; then
      return 0
    fi
  fi

  # Special handling for datetime validation errors
  if [[ "$needle" == *"is not valid date-time"* && "$haystack" == *"is not valid date-time"* ]]; then
    return 0
  fi

  # Match on just the core constraint message (e.g., "exclusiveMinimum: got -1.23, want 0")
  local needle_core haystack_core
  needle_core=$(echo "$needle" | grep -oE '[a-zA-Z]+: got .+, want .+|value must be .+|is not valid [a-zA-Z-]+')
  haystack_core=$(echo "$haystack" | grep -oE '[a-zA-Z]+: got .+, want .+|value must be .+|is not valid [a-zA-Z-]+')

  if [[ -n "$needle_core" && -n "$haystack_core" && "$needle_core" == "$haystack_core" ]]; then
    return 0
  fi

  return 1
}

function schema() {
  print_section "VERIFYING per-theme-type schemas"

  # Generate and verify all registered theme-type schemas
  local theme_types
  theme_types=$(uv run python -m packages.overture-schema.src.overture.schema --list-types 2>/dev/null | grep -E "^  [a-z]+:[a-z_]+$" | sed 's/^  //' || true)

  if [[ -z "$theme_types" ]]; then
    print_failure "FAILED - No theme-type combinations found"
    exit 1
  fi

  local failed_count=0
  while IFS= read -r theme_type; do
    if [[ -n "$theme_type" ]]; then
      local theme="${theme_type%:*}"
      local type="${theme_type#*:}"
      local schema_file="$temp_schema_dir/overture-schema-${theme}-${type}.json"

      # Generate schema if needed
      if [[ ! -f "$schema_file" ]] || [[ "$schema_file" -ot "$process_start_ref" ]]; then
        if ! uv run python -m packages.overture-schema.src.overture.schema --theme "$theme" --type "$type" > "$schema_file" 2>/dev/null; then
          print_status "FAILED" "overture-schema-${theme}-${type}.json" "(generation failed)"
          ((failed_count++))
          continue
        fi
      fi

      # Verify schema
      if jv --assert-format --assert-content "$schema_file" >/dev/null 2>/dev/null; then
        print_status "OK" "overture-schema-${theme}-${type}.json"
      else
        print_status "FAILED" "overture-schema-${theme}-${type}.json"
        printf "\n${RED}schema %s is invalid.${RESET}\n" "overture-schema-${theme}-${type}.json"
        ((failed_count++))
      fi
    fi
  done <<< "$theme_types"

  if [[ $failed_count -gt 0 ]]; then
    printf "\n${RED}%d schema(s) failed validation${RESET}\n" "$failed_count"
    exit 1
  fi
}

function examples() {
  print_section "VERIFYING examples"
  find reference/examples -type f | sort | while read -r instance_file; do
    if ! [[ "$instance_file" == *.yaml ]] && ! [[ "$instance_file" == *.json ]]; then
      print_status "FAILED" "$instance_file"
      printf "${RED}example instance '%s' is EXPECTED to be a .yaml or .json file but ACTUALLY it is not.${RESET}\n" "$instance_file"
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
        schema_info=" ${DIM}[${theme_type}]${RESET}"
      fi
    fi

    printf "%s%s..." "$instance_file" "$schema_info"
    if verify quiet "$instance_file"; then
      printf "${GREEN}OK${RESET}\n"
    else
      printf "${RED}FAILED${RESET}\n"
      printf "\n${RED}example instance '%s' is EXPECTED to pass validation but ACTUALLY it failed.${RESET}\n" "$instance_file"

      verify detailed "$instance_file"
    fi
  done
}

function counterexamples() {
  print_section "VERIFYING counterexamples"
  yq_installed=
  if command -v yq >/dev/null; then
    yq_installed=true
  else
    >&2 printf "${YELLOW}WARNING: yq is not installed. Install yq for higher-fidelity counterexample testing.${RESET}\n"
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
        schema_info=" ${DIM}[${theme_type}]${RESET}"
      fi
    fi

    printf "%s%s..." "$instance_file" "$schema_info"
    declare -a expected_errors
    if verify quiet "$instance_file"; then
      printf "${RED}FAILED${RESET}\n"
      printf "\n${RED}counterexample instance '%s' is EXPECTED to fail validation but ACTUALLY it passed.${RESET}\n" "$instance_file"

    elif [ -z "$yq_installed" ] || ! expected_errors "$instance_file" | mapfile -t expected_errors || [ ${#expected_errors} == 0 ]; then
      printf "${GREEN}OK${RESET}\n"
    else
      declare -a actual_errors
      (verify simple "$instance_file" || true) 2>&1 | mapfile -t actual_errors
      for expected_error in "${expected_errors[@]}"; do
        for actual_error in "${actual_errors[@]}"; do
          if flexible_contains "$actual_error" "$expected_error"; then
            continue 2
          fi
        done
        printf "${RED}FAILED${RESET}\n"
        printf "\n${RED}counterexample instance '%s' is EXPECTED to trigger the following validation error but ACTUALLY it did not.${RESET}\n\n" "$instance_file"
        printf "${YELLOW}%s${RESET}\n" "------------------------ MISSED EXPECTED ERROR -----------------------"
        printf "${YELLOW}%s${RESET}\n\n" "$expected_error"
        printf "${CYAN}%s${RESET}\n" "---------------------- ACTUAL VALIDATION OUTPUT ----------------------"
        printf "%s\n" "${actual_errors[@]}"
      done
      printf "${GREEN}OK${RESET}\n"
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
