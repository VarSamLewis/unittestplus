
def _clean_and_format_definition(definition: str) -> str:
    """
    Clean and format a function definition string to fix common issues.
    Specifically handles the format with spaces instead of newlines.
    """
    if not definition.strip():
        raise ValueError("Empty function definition")
    
    cleaned = definition.replace('\\"', '"').replace("\\'", "'")
    

    if '\n' not in cleaned:
        parts = []
        current_part = ""
        i = 0
        
        while i < len(cleaned):

            if cleaned[i:i+8] == '        ': 
                if current_part.strip():
                    parts.append(current_part.strip())
                current_part = ""
                i += 8
                # Skip any additional spaces
                while i < len(cleaned) and cleaned[i] == ' ':
                    i += 1
            elif cleaned[i:i+12] == '            ':  # 12 spaces = deeper indentation
                if current_part.strip():
                    parts.append(current_part.strip())
                current_part = ""
                i += 12
                # Skip any additional spaces
                while i < len(cleaned) and cleaned[i] == ' ':
                    i += 1
            else:
                current_part += cleaned[i]
                i += 1

        if current_part.strip():
            parts.append(current_part.strip())
        

        if parts:
            formatted_lines = []
            
            # First part should be the function definition
            if parts[0].startswith('def '):
                formatted_lines.append(parts[0])
                
                # Process remaining parts
                for part in parts[1:]:
                    if part.startswith('if ') or part.startswith('elif ') or part.startswith('else:') or \
                       part.startswith('for ') or part.startswith('while ') or part.startswith('try:') or \
                       part.startswith('except ') or part.startswith('finally:'):
                        # Control structure - base indentation
                        formatted_lines.append('    ' + part)
                    elif part.startswith('return ') or part.startswith('raise ') or part.startswith('pass'):
                        if formatted_lines and any(formatted_lines[-1].strip().startswith(kw) for kw in ['if ', 'elif ', 'else:', 'for ', 'while ', 'try:', 'except ', 'finally:']):
                            # This should be indented further (nested under control structure)
                            formatted_lines.append('        ' + part)
                        else:
                            # This is at function body level
                            formatted_lines.append('    ' + part)
                    else:
                        # Default to function body indentation
                        formatted_lines.append('    ' + part)
            
            cleaned = '\n'.join(formatted_lines)
    
    return cleaned


def _rebuild_function_from_definition(definition: str, func_name: str):
    """
    Rebuild a function from its string definition with proper error handling.
    """
    try:
        # Clean up the definition string
        cleaned_definition = _clean_and_format_definition(definition)
        
        # Debug: print the cleaned definition
        # print(f"Debug - Cleaned definition for {func_name}:")
        # print(repr(cleaned_definition))
        # print("Formatted:")
        # print(cleaned_definition)
        # print("-" * 50)
        
        namespace = {}
        
        exec(cleaned_definition, namespace)

        if func_name in namespace:
            return namespace[func_name]
        else:
            raise ValueError(f"Function '{func_name}' not found in definition")
            
    except SyntaxError as e:
        raise SyntaxError(f"Invalid function definition for '{func_name}': {e}")
    except Exception as e:
        raise RuntimeError(f"Error rebuilding function '{func_name}': {e}")