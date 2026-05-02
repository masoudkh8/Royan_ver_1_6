# debug_structure.py
import os
import importlib.util

print("=" * 50)
print("🔍 بررسی ساختار پروژه")
print("=" * 50)

# لیست filesی پایتون در روت
py_files = [f for f in os.listdir('.') if f.endswith('.py')]
print(f"\n📄 filesی .py in stock: {py_files}")

# بررسی هر file
for file in py_files:
    module_name = file[:-3]  # Delete .py
    try:
        spec = importlib.util.spec_from_file_location(module_name, file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # بررسی وجود متغیرهای رایج فلوریان
        flask_vars = ['app', 'application', 'flask_app']
        found = [var for var in flask_vars if hasattr(module, var)]
        
        if found:
            print(f"\n✅ file {file}:")
            print(f"   متغیرهای پیدا شده: {found}")
            
            # بررسی نوع متغیر
            for var in found:
                obj = getattr(module, var)
                print(f"   {var} نوع: {type(obj).__name__}")
                
    except Exception as e:
        print(f"\n❌ file {file}: Error - {e}")

print("\n" + "=" * 50)