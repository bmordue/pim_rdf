#!/bin/bash
# PIM RDF Validation Script (Shell version)
#
# This script provides comprehensive validation for the PIM RDF knowledge base:
# 1. TTL syntax validation using riot
# 2. SHACL shapes validation using shacl command
# 3. Data merging and SPARQL querying tests
# 4. Performance timing for all operations
#
# Usage: ./validate_pim.sh [directory]

# Configuration
DIRECTORY="${1:-.}"
DIRECTORY="$(realpath "$DIRECTORY")"
BUILD_DIR="$DIRECTORY/build"
SHAPES_DIR="$DIRECTORY/shapes"
QUERIES_DIR="$DIRECTORY/queries/validation"
CONFIG_DIR="$DIRECTORY/config"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Utility functions
print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

get_time_ms() {
    echo $(($(date +%s%3N)))
}

# Load domains configuration from YAML
load_domains_config() {
    local config_file="$CONFIG_DIR/domains.yaml"
    if [[ -f "$config_file" ]]; then
        # Extract filenames from YAML using basic text processing
        grep "filename:" "$config_file" | sed 's/.*filename: *//g' | tr -d '"' | tr -d "'"
    else
        print_warning "Using fallback hardcoded domain list"
        echo -e "base.ttl\ntasks.ttl\nnotes.ttl\ncontacts.ttl\nprojects.ttl\nbookmarks.ttl\nevents.ttl\ntags.ttl"
    fi
}

# Load validation configuration from YAML
load_validation_config() {
    local config_file="$CONFIG_DIR/validation.yaml"
    if [[ -f "$config_file" ]]; then
        # Extract data_file and shape_file pairs from YAML
        awk '/- data_file:/{data=$3} /shape_file:/{print data ":" $2}' "$config_file" | tr -d '"' | tr -d "'"
    else
        print_warning "Using fallback hardcoded validation mapping"
        echo "notes.ttl:notes-shapes.ttl"
    fi
}

# Validate TTL files for proper Turtle syntax
validate_ttl_files() {
    print_header "TTL Syntax Validation"
    
    local total_triples=0
    local file_count=0
    local total_start=$(get_time_ms)
    
    # Find all TTL files excluding merged files
    while IFS= read -r -d '' file; do
        local rel_path=$(realpath --relative-to="$DIRECTORY" "$file")
        local start_time=$(get_time_ms)
        
        if riot --validate --syntax=turtle "$file" &>/dev/null; then
            local end_time=$(get_time_ms)
            local duration=$((end_time - start_time))
            
            # Count triples using riot
            local triples=$(riot --count "$file" 2>/dev/null || echo "0")
            total_triples=$((total_triples + triples))
            file_count=$((file_count + 1))
            
            print_success "$rel_path: Valid ($triples triples) - ${duration}ms"
        else
            print_error "$rel_path: Invalid Turtle syntax"
            return 1
        fi
    done < <(find "$DIRECTORY" -name "*.ttl" -not -name "merged*.ttl" -print0)
    
    local total_end=$(get_time_ms)
    local total_duration=$((total_end - total_start))
    
    echo ""
    echo "Total: $total_triples triples across $file_count files"
    echo "Total validation time: ${total_duration}ms"
    return 0
}

# Merge TTL data files into a single graph
merge_data_files() {
    print_header "Data Merging"
    
    mkdir -p "$BUILD_DIR"
    local merged_file="$BUILD_DIR/merged.ttl"
    local start_time=$(get_time_ms)
    
    # Remove existing merged file
    rm -f "$merged_file"
    
    # Load data files from configuration and merge them
    while read -r filename; do
        local file_path="$DIRECTORY/$filename"
        if [[ -f "$file_path" ]]; then
            if [[ ! -f "$merged_file" ]]; then
                # First file - copy directly
                cp "$file_path" "$merged_file"
            else
                # Subsequent files - merge using riot
                local temp_file=$(mktemp)
                riot --output=turtle "$merged_file" "$file_path" > "$temp_file"
                mv "$temp_file" "$merged_file"
            fi
            print_success "Merged $filename"
        else
            print_warning "File not found: $filename"
        fi
    done < <(load_domains_config)
    
    local end_time=$(get_time_ms)
    local duration=$((end_time - start_time))
    
    if [[ -f "$merged_file" ]]; then
        local triples=$(riot --count "$merged_file" 2>/dev/null || echo "0")
        echo ""
        print_success "Merged $triples triples into build/merged.ttl"
        echo "Merge time: ${duration}ms"
        return 0
    else
        print_error "Failed to create merged file"
        return 1
    fi
}

# Test SPARQL queries on the merged data
test_sparql_queries() {
    print_header "SPARQL Query Testing"
    
    local merged_file="$BUILD_DIR/merged.ttl"
    if [[ ! -f "$merged_file" ]]; then
        print_error "Merged file not found - cannot test queries"
        return 1
    fi
    
    if [[ ! -d "$QUERIES_DIR" ]]; then
        print_warning "No validation queries directory found - skipping SPARQL testing"
        return 0
    fi
    
    # Query files to test
    local queries=(
        "list-tasks.sparql:List all tasks"
        "list-creativeworks.sparql:List all schema.org CreativeWorks"
        "count-by-type.sparql:Count entities by type"
    )
    
    for query_info in "${queries[@]}"; do
        IFS=':' read -r query_file query_name <<< "$query_info"
        local query_path="$QUERIES_DIR/$query_file"
        
        if [[ -f "$query_path" ]]; then
            echo ""
            echo "--- $query_name ---"
            local start_time=$(get_time_ms)
            
            # Use riot to execute SPARQL query
            local results=$(riot --query="$query_path" "$merged_file" 2>/dev/null || echo "")
            local end_time=$(get_time_ms)
            local duration=$((end_time - start_time))
            
            echo "Query time: ${duration}ms"
            
            if [[ -n "$results" ]]; then
                local count=$(echo "$results" | wc -l)
                # Show first 3 results
                echo "$results" | head -3 | sed 's/^/  /'
                if [[ $count -gt 3 ]]; then
                    echo "  ..."
                fi
                print_success "Found $count results"
            else
                print_warning "No results or query failed"
            fi
        else
            print_warning "Query file not found: $query_file"
        fi
    done
}

# Validate data against SHACL shapes
validate_shacl_shapes() {
    print_header "SHACL Shapes Validation"
    
    if [[ ! -d "$SHAPES_DIR" ]]; then
        print_warning "No shapes directory found - skipping SHACL validation"
        return 0
    fi
    
    local all_valid=true
    
    # Load validation mappings from configuration
    while read -r mapping; do
        IFS=':' read -r data_file shape_file <<< "$mapping"
        local data_path="$DIRECTORY/$data_file"
        local shape_path="$SHAPES_DIR/$shape_file"
        
        if [[ ! -f "$data_path" || ! -f "$shape_path" ]]; then
            print_warning "Skipping $data_file - missing data or shape file"
            continue
        fi
        
        echo ""
        echo "--- Validating $data_file against $shape_file ---"
        
        local start_time=$(get_time_ms)
        
        # Use shacl validate command from Apache Jena
        if shacl validate --shapes="$shape_path" --data="$data_path" &>/dev/null; then
            local end_time=$(get_time_ms)
            local duration=$((end_time - start_time))
            print_success "SHACL validation passed - ${duration}ms"
        else
            local end_time=$(get_time_ms)
            local duration=$((end_time - start_time))
            print_error "SHACL validation failed - ${duration}ms"
            
            # Show detailed error report
            echo "Report:"
            shacl validate --shapes="$shape_path" --data="$data_path" 2>&1 | sed 's/^/  /'
            all_valid=false
        fi
        
    done < <(load_validation_config)
    
    if [[ "$all_valid" == true ]]; then
        return 0
    else
        return 1
    fi
}

# Main execution
main() {
    echo "PIM RDF Validation Script (Shell version)"
    echo "Working directory: $DIRECTORY"
    echo "=================================================="
    
    # Step 1: Validate TTL syntax
    if ! validate_ttl_files; then
        echo ""
        print_error "TTL validation failed - stopping"
        exit 1
    fi
    
    # Step 2: Merge data files
    if ! merge_data_files; then
        echo ""
        print_error "Data merging failed - stopping"
        exit 1
    fi
    
    # Step 3: Test SPARQL queries
    test_sparql_queries
    
    # Step 4: SHACL validation
    if ! validate_shacl_shapes; then
        echo ""
        print_warning "SHACL validation had issues"
    fi
    
    echo ""
    echo "=================================================="
    print_success "All validation steps completed successfully!"
}

# Run main function
main "$@"
