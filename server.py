from mcp.server.fastmcp import FastMCP
import requests
import execjs

mcp = FastMCP()

@mcp.tool()
def usage_guide() -> str:
    """
    完整使用指南：
    
    === BUPT 教务系统 ===
    1) 首先调用 login_to_BUPT_website(username, password) 完成首次登录
    2) 可用 check_is_login() 检查登录态，返回 Login successful/failed
    3) 获取页面内容请用 get_page_content_in_BUPT_website(url)
    注意：URL 必须位于 https://jwgl.bupt.edu.cn/jsxsd/ 域名下
    
    === BUPT 信息门户系统 ===
    1) 设置cookies供之后使用
    2) 检查登录：check_is_login_in_BUPT_Menhu_website()
    3) 获取内容：get_page_content_in_BUPT_Menhu_website(url)
    
    === 登录类型说明 ===
    - 教务系统需要使用用户名和密码
    - 信息门户需要设置cookies
    
    === 安全提醒 ===
    - 不要在日志/响应中回显密码或验证码
    - 两个系统的登录状态是独立的
    """
    return """
    完整使用指南：
    
    === BUPT 教务系统 ===
    1) 首先调用 login_to_BUPT_website(username, password) 完成首次登录
    2) 可用 check_is_login() 检查登录态，返回 Login successful/failed  
    3) 获取页面内容请用 get_page_content_in_BUPT_website(url)
    注意：URL 必须位于 https://jwgl.bupt.edu.cn/jsxsd/ 域名下
    
    === BUPT 信息门户系统 ===
    1) 密码登录：login_new_website_with_password(username, password)
    2) 检查登录：check_new_website_login()
    3) 获取内容：get_new_website_content(url)
    
    === 登录类型说明 ===
    - username_password: 用户名密码登录
    - username_smstoken: 用户名短信验证码登录
    
    === 安全提醒 ===
    - 不要在日志/响应中回显密码或验证码
    - 两个系统的登录状态是独立的
    """
# 教务系统登录管理类
class JiaoWuWebLogin:
    def __init__(self):
        self.url = "https://jwgl.bupt.edu.cn/jsxsd/"
        self.session = requests.Session()
        self.session.get(self.url)
        self.username = "" # student id
        self.password = "" # password
        self.is_login = False

    def GetEncoded(self): # get encoded string
        with open("conwork.js",encoding = 'utf-8') as f:
            js = execjs.compile(f.read())
            encoded =  js.call('encode',self.username,self.password)
            f.close()
        return encoded # return encoded string
    def login(self) -> bool:
        encoded = self.GetEncoded()
        postData = {
            'encoded': encoded.strip()
        }
        response = self.session.post(self.url + "xk/LoginToXk", data=postData)
        return response

# 门户网站登录管理类
class MenhuWebLogin:
    """BUPT 信息门户"""
    
    def __init__(self):
        self.session = requests.Session()
        self.cookies_set = False
        
        # 设置浏览器头，模拟真实浏览器访问
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def set_cookies_from_string(self, cookie_string: str, domain: str = "bupt.edu.cn") -> dict:
        """
        从 cookie 字符串设置 cookies
        
        Args:
            cookie_string: cookie 字符串，格式如 "name1=value1; name2=value2"
            domain: cookie 的域名
            
        Returns:
            dict: 操作结果
        """
        try:
            # 解析 cookie 字符串
            cookies = {}
            for item in cookie_string.split(';'):
                if '=' in item:
                    name, value = item.strip().split('=', 1)
                    cookies[name.strip()] = value.strip()
            
            # 设置到 session 中
            for name, value in cookies.items():
                self.session.cookies.set(name, value, domain=domain)
            
            self.cookies_set = True
            return {
                "ok": True, 
                "message": f"成功设置 {len(cookies)} 个 cookie",
                "cookies": cookies
            }
            
        except Exception as e:
            return {"ok": False, "error": f"设置 cookie 失败: {str(e)}"}

# 创建教务系统登录实例
mylogin = JiaoWuWebLogin()

# 创建新网页登录实例
menhu_web_login = MenhuWebLogin()

@mcp.tool()
def login_to_BUPT_JiaoWu_website(context: dict) -> str:
    """
    Login to the website.  
    This is the first login, it will let you to get the access to the website.
    You don't need to run this tool anymore, unless you want to change your username or password.
    Args:
        username: The username to login with.
        password: The password to login with.

    Returns:
        The result of the login.
    """
    username = context.get('username')
    password = context.get('password')
    mylogin.username = username
    mylogin.password = password
    if mylogin.login().status_code == 200:
        mylogin.is_login = True
        return {"ok": True, "message": "Login successful"}
    else:
        return {"ok": False, "message": "Login failed"} 

@mcp.tool()
def check_is_login_in_BUPT_JiaoWu_website(context: dict) -> dict:
    """
    Check if you are logged in.
    Returns:
        The result of the login.
        If you are logged in, it will return "Login successful".
        If you are not logged in, it will return "Login failed" and you need to run login_to_BUPT_website tool again.
    """
    return {"ok": True, "message": "Login successful"} if mylogin.is_login else {"ok": False, "message": "Login failed"}    

@mcp.tool()
def get_page_content_in_BUPT_JiaoWu_website(context: dict) -> dict:
    """
    Get the content of a page in BUPT.
    Must be logged in first.(run login_to_BUPT_website tool first)
    You just need to provide the url of the page you want to get the content of.
    Args:
        url: The URL of the page to get the content of.
    Returns:
        The content of the page.
    """
    url = context.get('url')
    if not url:
        return {"ok": False, "message": "Error: No URL provided in context."}
    return {"ok": True, "content": mylogin.session.get(url, timeout=10.0, allow_redirects=True).text}

@mcp.tool()
def set_cookies_in_BUPT_Menhu_website(context: dict) -> dict:
    """
    设置门户网站的cookies。
    
    Args:
        cookies: 门户网站的cookies
        
    Returns:
        dict: {"ok": bool, "message": str, "cookies": dict} 或 {"ok": bool, "error": str}
        
    使用示例:
        - 首次登录需要提供 cookies
        - 成功后可以调用其他门户网站相关工具
    """
    cookies = context.get('cookies')
    return menhu_web_login.set_cookies_from_string(cookies)

@mcp.tool()
def check_is_login_in_BUPT_Menhu_website(context: dict) -> dict:
    """
    检查门户网站的登录状态。
    Returns:
        dict: {"ok": bool, "logged_in": bool}
    """
    return {
        "ok": True,
        "logged_in": menhu_web_login.cookies_set 
        }

@mcp.tool()
def get_page_content_in_BUPT_Menhu_website(context: dict) -> dict:
    """
    获取门户网站的页面内容。
    你需要告知用户的全部通知/文件的内容,帮助用户理解此文章的含义.
    Args:
        url: 要获取内容的页面URL
        
    Returns:
        dict: {"ok": bool, "content": str} 或 {"ok": bool, "error": str}
        
    前置条件:
        - 必须先使用 set_cookies_in_BUPT_Menhu_website 设置cookies
    """
    url = context.get('url')
    return menhu_web_login.session.get(url, timeout=10.0, allow_redirects=True).text

if __name__ == "__main__":
    mcp.run()