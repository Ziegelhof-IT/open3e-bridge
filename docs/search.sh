#!/bin/bash
# Full-text search across all downloaded docs
# Usage: ./docs/search.sh <pattern> [options]
#
# Examples:
#   ./docs/search.sh "DID 268"
#   ./docs/search.sh "Kompressor" -i
#   ./docs/search.sh "O3EEnum" --context 3
#   ./docs/search.sh "COP" --type pdf
#   ./docs/search.sh "DoIP" --type discussions

set -uo pipefail

DOCS_DIR="$(cd "$(dirname "$0")" && pwd)"
DOWNLOADS="$DOCS_DIR/downloads"

usage() {
    echo "Usage: $0 <pattern> [options]"
    echo ""
    echo "Options:"
    echo "  -i, --ignore-case   Case-insensitive search"
    echo "  -c, --context N     Show N lines of context (default: 2)"
    echo "  -l, --files-only    Show only filenames"
    echo "  --type TYPE         Filter by type: discussions, issues, wiki, forums,"
    echo "                      community, web, pdfs, github-projects, all (default)"
    echo "  --stats             Show match counts per directory"
    echo "  -h, --help          Show this help"
    exit 0
}

PATTERN=""
CASE_FLAG=""
CONTEXT=2
FILES_ONLY=""
TYPE="all"
STATS=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        -i|--ignore-case) CASE_FLAG="-i"; shift ;;
        -c|--context) CONTEXT="$2"; shift 2 ;;
        -l|--files-only) FILES_ONLY="-l"; shift ;;
        --type) TYPE="$2"; shift 2 ;;
        --stats) STATS="1"; shift ;;
        -h|--help) usage ;;
        *) PATTERN="$1"; shift ;;
    esac
done

if [[ -z "$PATTERN" ]]; then
    echo "Error: No search pattern provided"
    usage
fi

# Build search paths based on type
PATHS=()
case "$TYPE" in
    discussions) PATHS=("$DOWNLOADS/github/discussions") ;;
    issues)      PATHS=("$DOWNLOADS/github/issues") ;;
    wiki)        PATHS=("$DOWNLOADS/github/wiki") ;;
    forums)      PATHS=("$DOWNLOADS/forums") ;;
    community)   PATHS=("$DOWNLOADS/community") ;;
    web)         PATHS=("$DOWNLOADS/web") ;;
    pdfs)        PATHS=("$DOWNLOADS/pdfs") ;;
    github-projects) PATHS=("$DOWNLOADS/github") ;;
    all)         PATHS=(
                     "$DOWNLOADS/github/discussions"
                     "$DOWNLOADS/github/issues"
                     "$DOWNLOADS/github/wiki"
                     "$DOWNLOADS/forums"
                     "$DOWNLOADS/community"
                     "$DOWNLOADS/web"
                     "$DOWNLOADS/pdfs"
                     "$DOCS_DIR/OPEN3E_TECHNICAL_REFERENCE.md"
                     "$DOCS_DIR/VITOCAL_250A_DOCUMENTATION.md"
                 ) ;;
    *) echo "Unknown type: $TYPE"; exit 1 ;;
esac

# Include only text-searchable files
INCLUDE="--include=*.md --include=*.txt --include=*.html --include=*.yaml --include=*.yml"

if [[ -n "$STATS" ]]; then
    echo "=== Match counts for: $PATTERN ==="
    for p in "${PATHS[@]}"; do
        if [[ -e "$p" ]]; then
            count=$(grep -r $CASE_FLAG $INCLUDE -c "$PATTERN" "$p" 2>/dev/null | awk -F: '{s+=$NF} END {print s+0}')
            name=$(basename "$p")
            [[ -f "$p" ]] && name=$(basename "$p")
            printf "  %-30s %d matches\n" "$name" "$count"
        fi
    done
    exit 0
fi

if [[ -n "$FILES_ONLY" ]]; then
    for p in "${PATHS[@]}"; do
        [[ -e "$p" ]] && grep -rl $CASE_FLAG $INCLUDE "$PATTERN" "$p" 2>/dev/null || true
    done | sort
else
    for p in "${PATHS[@]}"; do
        [[ -e "$p" ]] && grep -rn $CASE_FLAG $INCLUDE -C "$CONTEXT" --color=always "$PATTERN" "$p" 2>/dev/null || true
    done
fi
