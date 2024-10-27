from typing import Dict, Any, Optional

class EnvValidator:
    def __init__(self):
        self.schemas = {}
    
    def add_schema(self, var_name: str, var_type: type, required: bool = True):
        self.schemas[var_name] = {
            'type': var_type,
            'required': required
        }
    
    def validate(self, env_vars: Dict[str, Any]) -> bool:
     
        for var_name, schema in self.schemas.items():
            if var_name not in env_vars:
                if schema['required']:
                   
                    raise ValueError(f"Missing required env var: {var_name}")
                continue
            
            value = env_vars[var_name]
            try:
                schema['type'](value)
            except ValueError:
                raise ValueError(f"Invalid type for {var_name}: {value}")
        
        return True
