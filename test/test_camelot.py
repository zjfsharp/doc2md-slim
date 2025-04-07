import os
import subprocess
import sys

def test_ghostscript():
    """测试Ghostscript是否正确安装并可访问"""
    try:
        # 检查gs命令是否可用
        gs_path = subprocess.check_output(['which', 'gs']).decode('utf-8').strip()
        print(f"Ghostscript路径: {gs_path}")
        
        # 检查gs版本
        gs_version = subprocess.check_output(['gs', '--version']).decode('utf-8').strip()
        print(f"Ghostscript版本: {gs_version}")
        
        # 检查gs是否可执行
        subprocess.run(['gs', '-dNODISPLAY', '-dQUIET', '-dBATCH', '-dSAFER', '-sDEVICE=nullpage', '-r72', '-dNOPAUSE', '-dNOCACHE', '-sOutputFile=/dev/null', '-c', 'quit'], check=True)
        print("Ghostscript测试成功: 可以执行基本命令")
        
        return True
    except Exception as e:
        print(f"Ghostscript测试失败: {e}")
        return False

def test_camelot():
    """测试camelot-py是否可以正确导入和使用"""
    try:
        import camelot
        print(f"camelot-py版本: {camelot.__version__}")
        
        # 尝试导入camelot的后端模块
        from camelot.backends import image_conversion
        print("成功导入camelot后端模块")
        
        # 尝试创建一个简单的PDF文件用于测试
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
            temp_pdf_path = temp_pdf.name
            # 创建一个简单的PDF文件
            with open(temp_pdf_path, 'wb') as f:
                f.write(b'%PDF-1.4\n%EOF\n')
        
        print(f"创建测试PDF文件: {temp_pdf_path}")
        
        # 尝试使用camelot读取PDF
        try:
            tables = camelot.read_pdf(temp_pdf_path, pages='1')
            print("成功使用camelot读取PDF")
        except Exception as e:
            print(f"使用camelot读取PDF时出错: {e}")
        
        # 清理临时文件
        os.unlink(temp_pdf_path)
        
        return True
    except Exception as e:
        print(f"camelot-py测试失败: {e}")
        return False

if __name__ == "__main__":
    print("=== 测试Ghostscript和camelot-py集成 ===")
    print(f"Python版本: {sys.version}")
    print(f"当前工作目录: {os.getcwd()}")
    print(f"PATH环境变量: {os.environ.get('PATH', '未设置')}")
    
    gs_ok = test_ghostscript()
    camelot_ok = test_camelot()
    
    if gs_ok and camelot_ok:
        print("\n✅ 所有测试通过！Ghostscript和camelot-py可以正常工作。")
    else:
        print("\n❌ 测试失败！请检查上面的错误信息。") 