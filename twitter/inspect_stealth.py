import playwright_stealth.stealth as stealth_module
with open("inspection_result.txt", "w") as f:
    if hasattr(stealth_module, 'async_api'):
        f.write(f"async_api dir: {dir(stealth_module.async_api)}\n")
    else:
        f.write("async_api not found in stealth module\n")
        
    if hasattr(stealth_module, 'Stealth'):
        f.write(f"Stealth dir: {dir(stealth_module.Stealth)}\n")
