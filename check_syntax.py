"""
簡單的語法檢查 - 驗證所有Python文件是否有語法錯誤
"""
import py_compile
import os

def check_file(filepath):
    """檢查單個文件的語法"""
    try:
        py_compile.compile(filepath, doraise=True)
        return True, None
    except py_compile.PyCompileError as e:
        return False, str(e)

def main():
    """檢查所有Python文件"""
    print("=" * 60)
    print("檢查Python文件語法")
    print("=" * 60)
    
    src_dir = "src"
    errors = []
    success_count = 0
    
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                relative_path = os.path.relpath(filepath)
                
                success, error = check_file(filepath)
                if success:
                    print(f"✓ {relative_path}")
                    success_count += 1
                else:
                    print(f"✗ {relative_path}")
                    print(f"  錯誤: {error}")
                    errors.append((relative_path, error))
    
    print("\n" + "=" * 60)
    print("檢查結果")
    print("=" * 60)
    print(f"成功: {success_count} 個文件")
    print(f"失敗: {len(errors)} 個文件")
    
    if errors:
        print("\n語法錯誤列表:")
        for filepath, error in errors:
            print(f"  - {filepath}")
    else:
        print("\n🎉 所有文件語法正確！")
    
    return len(errors) == 0

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
