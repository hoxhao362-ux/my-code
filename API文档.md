# /api/sub/v1
说明：这是投稿站用的API接口，所有投稿站相关的操作都需要通过这个接口进行。
## /user
说明：这是用户相关的API接口，包括用户登录和注册。
- /login
    - POST
     - username: str = Field(..., description="用户名")
     - password: str = Field( ...,
            description="密码规则：8-20位，含大小写字母+数字，可使用!@#$%^&*()_+-={}[]:;\"'<>,.?~`等特殊字符，禁止|\\/和中文",
            pattern=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d!@#$%^&*()_+\-={}[\]:;\"'<>,.?~`]{8,20}$"
        )
     - is_remember: bool = Field(False, description="是否记住登录状态")
    - 返回值：
     - login_time: datetime.datetime = Field(default_factory=datetime.datetime.now, description="登录时间")
     - is_remember: bool = Field(False, description="是否记住登录状态")
     - token: str = Field(..., description="登录凭证")
    备注：登录凭证需要在后续的请求中携带，用于验证用户身份。密码前端需要加密后传输。

说明：用户登录接口，需要提供用户名、密码、邮箱。
- /register
    - POST
      - username: str = Field(..., description="用户名")
      - password: str = Field(
        ...,
        description="密码规则：8-20位，含大小写字母+数字，可使用!@#$%^&*()_+-={}[]:;\"'<>,.?~`等特殊字符，禁止|\\/和中文",
        pattern=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d!@#$%^&*()_+\-={}[\]:;\"'<>,.?~`]{8,20}$"
    )
      - email: EmailStr = Field(..., description="注册邮箱")
     - register_time: datetime.datetime = Field(default_factory=datetime.datetime.now, description="注册时间")
     - token: str = Field(..., description="登录凭证")
    备注：注册时需要提供用户名、密码、邮箱等信息。密码前端需要加密后传输。

说明：用户注册接口，需要提供用户名、密码、邮箱等信息。

- /verify
    - POST
     - token: str = Field(..., description="注册凭证")
    备注：注册时需要提供注册凭证，用于验证邮箱。

## /admin

- /login
    - POST
     - username: str = Field(..., description="用户名")
     - password: str = Field(
        ...,
        description="密码规则：8-20位，含大小写字母+数字，可使用!@#$%^&*()_+-={}[]:;\"'<>,.?~`等特殊字符，禁止|\\/和中文",
        pattern=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d!@#$%^&*()_+\-={}[\]:;\"'<>,.?~`]{8,20}$"
    )
     - is_remember: bool = Field(False, description="是否记住登录状态")
    - 返回值：
     - login_time: datetime.datetime = Field(default_factory=datetime.datetime.now, description="登录时间")
     - is_remember: bool = Field(False, description="是否记住登录状态")
     - token: str = Field(..., description="登录凭证")
    备注：登录凭证需要在后续的请求中携带，用于验证管理员身份。密码前端需要加密后传输。
