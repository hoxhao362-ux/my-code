# 期刊平台API文档

## 文档说明
本文档描述了期刊平台的所有API接口，包括用户管理、文献管理、审稿管理和管理员功能。所有接口都遵循RESTful设计风格。

## API基础信息
- **基础URL**: `/api/v1`
- **认证方式**: JWT Token（除登录、注册接口外，其他接口需在请求中携带token参数）
- **响应格式**: JSON
- **错误处理**: 使用HTTP状态码和详细错误信息

## 模块分类

### 1. 用户相关接口 (`/user`)

#### 1.1 用户注册
- **URL**: `/user/register`
- **方法**: `POST`
- **请求参数**:
  | 参数名 | 类型 | 必填 | 描述 |
  |--------|------|------|------|
  | username | string | 是 | 用户名 |
  | password | string | 是 | 密码（8-20位，含大小写字母+数字，禁止|\/和中文） |
  | email | string | 是 | 注册邮箱 |
  | is_remember | boolean | 否 | 是否记住登录状态（默认：false） |

- **响应示例**:
  ```json
  {
    "register_time": "2025-12-24T10:00:00",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
  ```

- **错误码**:
  | 状态码 | 描述 |
  |--------|------|
  | 400 | 用户名已存在 / 邮箱已被注册 / 密码格式错误 |
  | 429 | 注册请求过于频繁 |

#### 1.2 用户登录
- **URL**: `/user/login`
- **方法**: `POST`
- **请求参数**:
  | 参数名 | 类型 | 必填 | 描述 |
  |--------|------|------|------|
  | username | string | 是 | 用户名 |
  | password | string | 是 | 密码 |
  | is_remember | boolean | 否 | 是否记住登录状态（默认：false） |

- **响应示例**:
  ```json
  {
    "login_time": "2025-12-24T10:00:00",
    "is_remember": true,
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
  ```

- **错误码**:
  | 状态码 | 描述 |
  |--------|------|
  | 401 | 用户名或密码错误 |
  | 429 | 登录请求过于频繁 |

#### 1.3 获取当前用户信息
- **URL**: `/user/me`
- **方法**: `GET`
- **请求参数**:
  | 参数名 | 类型 | 必填 | 描述 |
  |--------|------|------|------|
  | token | string | 是 | 登录凭证 |

- **响应示例**:
  ```json
  {
    "uid": 1,
    "username": "testuser",
    "email": "test@example.com",
    "role": "user",
    "create_time": "2025-12-24T10:00:00",
    "last_login_time": "2025-12-24T10:30:00",
    "avatar_hash": null,
    "is_online": true
  }
  ```

- **错误码**:
  | 状态码 | 描述 |
  |--------|------|
  | 401 | 无效的token |
  | 404 | 用户不存在 |

#### 1.4 用户登出
- **URL**: `/user/logout`
- **方法**: `POST`
- **请求参数**:
  | 参数名 | 类型 | 必填 | 描述 |
  |--------|------|------|------|
  | token | string | 是 | 登录凭证 |

- **响应示例**:
  ```json
  {
    "message": "登出成功"
  }
  ```

### 2. 文献相关接口 (`/journal`)

#### 2.1 上传文献
- **URL**: `/journal/upload`
- **方法**: `POST`
- **请求参数**:
  | 参数名 | 类型 | 必填 | 描述 |
  |--------|------|------|------|
  | token | string | 是 | 登录凭证 |
  | title | string | 是 | 文献标题 |
  | authors | string | 是 | 文献作者（多个作者用逗号分隔） |
  | abstract | string | 否 | 文献摘要 |
  | file | file | 是 | 文献文件（支持PDF和Word文档） |

- **响应示例**:
  ```json
  {
    "jid": 1,
    "title": "测试文献",
    "status": "pending",
    "upload_time": "2025-12-24T10:00:00"
  }
  ```

- **错误码**:
  | 状态码 | 描述 |
  |--------|------|
  | 401 | 无效的token |
  | 400 | 不支持的文件类型 |

#### 2.2 获取我的文献列表
- **URL**: `/journal/my`
- **方法**: `GET`
- **请求参数**:
  | 参数名 | 类型 | 必填 | 描述 |
  |--------|------|------|------|
  | token | string | 是 | 登录凭证 |
  | page | integer | 否 | 页码（默认：1） |
  | page_size | integer | 否 | 每页条数（默认：10） |

- **响应示例**:
  ```json
  {
    "total": 5,
    "journals": [
      {
        "jid": 1,
        "title": "测试文献",
        "authors": "张三,李四",
        "abstract": "这是一篇测试文献",
        "status": "pending",
        "file_name": "test.pdf",
        "file_size": 1024000,
        "upload_time": "2025-12-24T10:00:00",
        "update_time": "2025-12-24T10:00:00"
      }
    ]
  }
  ```

- **错误码**:
  | 状态码 | 描述 |
  |--------|------|
  | 401 | 无效的token |

#### 2.3 获取文献详情
- **URL**: `/journal/detail/{jid}`
- **方法**: `GET`
- **请求参数**:
  | 参数名 | 类型 | 必填 | 描述 |
  |--------|------|------|------|
  | token | string | 是 | 登录凭证 |
  | jid | integer | 是 | 文献ID |

- **响应示例**:
  ```json
  {
    "jid": 1,
    "title": "测试文献",
    "authors": "张三,李四",
    "abstract": "这是一篇测试文献",
    "status": "pending",
    "file_name": "test.pdf",
    "file_size": 1024000,
    "upload_time": "2025-12-24T10:00:00",
    "update_time": "2025-12-24T10:00:00"
  }
  ```

- **错误码**:
  | 状态码 | 描述 |
  |--------|------|
  | 401 | 无效的token |
  | 403 | 无权访问此文献 |
  | 404 | 文献不存在 |

#### 2.4 删除文献
- **URL**: `/journal/{jid}`
- **方法**: `DELETE`
- **请求参数**:
  | 参数名 | 类型 | 必填 | 描述 |
  |--------|------|------|------|
  | token | string | 是 | 登录凭证 |
  | jid | integer | 是 | 文献ID |

- **响应示例**:
  ```json
  {
    "message": "文献删除成功"
  }
  ```

- **错误码**:
  | 状态码 | 描述 |
  |--------|------|
  | 401 | 无效的token |
  | 403 | 无权删除此文献 |
  | 404 | 文献不存在 |

#### 2.5 获取公开文献列表
- **URL**: `/journal/public`
- **方法**: `GET`
- **请求参数**:
  | 参数名 | 类型 | 必填 | 描述 |
  |--------|------|------|------|
  | page | integer | 否 | 页码（默认：1） |
  | page_size | integer | 否 | 每页条数（默认：10） |

- **响应示例**:
  ```json
  {
    "total": 10,
    "journals": [
      {
        "jid": 1,
        "title": "测试文献",
        "authors": "张三,李四",
        "abstract": "这是一篇测试文献",
        "status": "approved",
        "file_name": "test.pdf",
        "file_size": 1024000,
        "upload_time": "2025-12-24T10:00:00",
        "update_time": "2025-12-24T11:00:00"
      }
    ]
  }
  ```

### 3. 审稿相关接口 (`/review`)

#### 3.1 获取待审核文献列表
- **URL**: `/review/pending`
- **方法**: `GET`
- **请求参数**:
  | 参数名 | 类型 | 必填 | 描述 |
  |--------|------|------|------|
  | token | string | 是 | 登录凭证 |
  | page | integer | 否 | 页码（默认：1） |
  | page_size | integer | 否 | 每页条数（默认：10） |

- **响应示例**:
  ```json
  {
    "total": 5,
    "journals": [
      {
        "jid": 1,
        "title": "测试文献",
        "authors": "张三,李四",
        "abstract": "这是一篇测试文献",
        "status": "pending",
        "file_name": "test.pdf",
        "file_size": 1024000,
        "upload_time": "2025-12-24T10:00:00",
        "update_time": "2025-12-24T10:00:00"
      }
    ]
  }
  ```

- **错误码**:
  | 状态码 | 描述 |
  |--------|------|
  | 401 | 无效的token |
  | 403 | 无权访问此接口 |

#### 3.2 审核文献
- **URL**: `/review/review/{jid}`
- **方法**: `POST`
- **请求参数**:
  | 参数名 | 类型 | 必填 | 描述 |
  |--------|------|------|------|
  | token | string | 是 | 登录凭证 |
  | jid | integer | 是 | 文献ID |
  | result | string | 是 | 审核结果（approved/rejected） |
  | comment | string | 否 | 审核意见 |

- **响应示例**:
  ```json
  {
    "message": "审核成功",
    "result": "approved",
    "comment": "文章质量良好，建议发表"
  }
  ```

- **错误码**:
  | 状态码 | 描述 |
  |--------|------|
  | 401 | 无效的token |
  | 403 | 无权访问此接口 |
  | 400 | 审核结果无效 / 该文献已被审核 |
  | 404 | 文献不存在 |

#### 3.3 获取审核历史记录
- **URL**: `/review/history`
- **方法**: `GET`
- **请求参数**:
  | 参数名 | 类型 | 必填 | 描述 |
  |--------|------|------|------|
  | token | string | 是 | 登录凭证 |
  | page | integer | 否 | 页码（默认：1） |
  | page_size | integer | 否 | 每页条数（默认：10） |

- **响应示例**:
  ```json
  {
    "total": 20,
    "records": [
      {
        "id": 1,
        "jid": 1,
        "reviewer_uid": 2,
        "review_time": "2025-12-24T11:00:00",
        "result": "approved",
        "comment": "文章质量良好",
        "title": "测试文献",
        "authors": "张三,李四",
        "status": "approved"
      }
    ]
  }
  ```

- **错误码**:
  | 状态码 | 描述 |
  |--------|------|
  | 401 | 无效的token |
  | 403 | 无权访问此接口 |

#### 3.4 获取审核统计信息
- **URL**: `/review/statistics`
- **方法**: `GET`
- **请求参数**:
  | 参数名 | 类型 | 必填 | 描述 |
  |--------|------|------|------|
  | token | string | 是 | 登录凭证 |

- **响应示例**:
  ```json
  {
    "total": 20,
    "approved": 15,
    "rejected": 5,
    "approval_rate": 0.75
  }
  ```

- **错误码**:
  | 状态码 | 描述 |
  |--------|------|
  | 401 | 无效的token |
  | 403 | 无权访问此接口 |

#### 3.5 获取被拒绝的文献列表
- **URL**: `/review/rejected`
- **方法**: `GET`
- **请求参数**:
  | 参数名 | 类型 | 必填 | 描述 |
  |--------|------|------|------|
  | token | string | 是 | 登录凭证 |
  | page | integer | 否 | 页码（默认：1） |
  | page_size | integer | 否 | 每页条数（默认：10） |

- **响应示例**:
  ```json
  {
    "total": 5,
    "journals": [
      {
        "jid": 2,
        "title": "不合格文献",
        "authors": "王五",
        "abstract": "这是一篇不合格的文献",
        "status": "rejected",
        "file_name": "bad.pdf",
        "file_size": 512000,
        "upload_time": "2025-12-23T15:00:00",
        "update_time": "2025-12-23T16:00:00",
        "comment": "内容不符合要求",
        "review_time": "2025-12-23T16:00:00"
      }
    ]
  }
  ```

- **错误码**:
  | 状态码 | 描述 |
  |--------|------|
  | 401 | 无效的token |
  | 403 | 无权访问此接口 |

### 4. 管理员相关接口 (`/admin`)

#### 4.1 获取用户列表
- **URL**: `/admin/users`
- **方法**: `GET`
- **请求参数**:
  | 参数名 | 类型 | 必填 | 描述 |
  |--------|------|------|------|
  | token | string | 是 | 登录凭证 |
  | page | integer | 否 | 页码（默认：1） |
  | page_size | integer | 否 | 每页条数（默认：10） |
  | role | string | 否 | 用户角色（user/reviewer/admin） |

- **响应示例**:
  ```json
  {
    "total": 100,
    "users": [
      {
        "uid": 1,
        "username": "admin",
        "email": "admin@example.com",
        "role": "admin",
        "is_verified": true,
        "create_time": "2025-12-20T09:00:00",
        "last_login_time": "2025-12-24T10:00:00"
      }
    ]
  }
  ```

- **错误码**:
  | 状态码 | 描述 |
  |--------|------|
  | 401 | 无效的token |
  | 403 | 无权访问此接口 |

#### 4.2 修改用户角色
- **URL**: `/admin/users/{uid}/role`
- **方法**: `PUT`
- **请求参数**:
  | 参数名 | 类型 | 必填 | 描述 |
  |--------|------|------|------|
  | token | string | 是 | 登录凭证 |
  | uid | integer | 是 | 用户ID |
  | role | string | 是 | 新角色（user/reviewer/admin） |

- **响应示例**:
  ```json
  {
    "message": "用户角色更新成功",
    "uid": 2,
    "new_role": "reviewer"
  }
  ```

- **错误码**:
  | 状态码 | 描述 |
  |--------|------|
  | 401 | 无效的token |
  | 403 | 无权访问此接口 |
  | 400 | 角色无效 |
  | 404 | 用户不存在 |

#### 4.3 删除用户
- **URL**: `/admin/users/{uid}`
- **方法**: `DELETE`
- **请求参数**:
  | 参数名 | 类型 | 必填 | 描述 |
  |--------|------|------|------|
  | token | string | 是 | 登录凭证 |
  | uid | integer | 是 | 用户ID |

- **响应示例**:
  ```json
  {
    "message": "用户删除成功",
    "uid": 3
  }
  ```

- **错误码**:
  | 状态码 | 描述 |
  |--------|------|
  | 401 | 无效的token |
  | 403 | 无权访问此接口 |
  | 404 | 用户不存在 |

#### 4.4 获取所有文献列表
- **URL**: `/admin/journals/all`
- **方法**: `GET`
- **请求参数**:
  | 参数名 | 类型 | 必填 | 描述 |
  |--------|------|------|------|
  | token | string | 是 | 登录凭证 |
  | page | integer | 否 | 页码（默认：1） |
  | page_size | integer | 否 | 每页条数（默认：10） |
  | status | string | 否 | 文献状态（pending/approved/rejected） |

- **响应示例**:
  ```json
  {
    "total": 50,
    "journals": [
      {
        "jid": 1,
        "title": "测试文献",
        "authors": "张三,李四",
        "abstract": "这是一篇测试文献",
        "status": "approved",
        "file_name": "test.pdf",
        "file_size": 1024000,
        "create_time": "2025-12-24T10:00:00",
        "update_time": "2025-12-24T11:00:00",
        "uploader": "zhangsan"
      }
    ]
  }
  ```

- **错误码**:
  | 状态码 | 描述 |
  |--------|------|
  | 401 | 无效的token |
  | 403 | 无权访问此接口 |

#### 4.5 删除文献
- **URL**: `/admin/journals/{jid}`
- **方法**: `DELETE`
- **请求参数**:
  | 参数名 | 类型 | 必填 | 描述 |
  |--------|------|------|------|
  | token | string | 是 | 登录凭证 |
  | jid | integer | 是 | 文献ID |

- **响应示例**:
  ```json
  {
    "message": "文献删除成功"
  }
  ```

- **错误码**:
  | 状态码 | 描述 |
  |--------|------|
  | 401 | 无效的token |
  | 403 | 无权访问此接口 |
  | 404 | 文献不存在 |

#### 4.6 获取所有审核记录
- **URL**: `/admin/review-records`
- **方法**: `GET`
- **请求参数**:
  | 参数名 | 类型 | 必填 | 描述 |
  |--------|------|------|------|
  | token | string | 是 | 登录凭证 |
  | page | integer | 否 | 页码（默认：1） |
  | page_size | integer | 否 | 每页条数（默认：10） |

- **响应示例**:
  ```json
  {
    "total": 100,
    "records": [
      {
        "id": 1,
        "jid": 1,
        "reviewer_uid": 2,
        "review_time": "2025-12-24T11:00:00",
        "result": "approved",
        "comment": "文章质量良好",
        "title": "测试文献",
        "reviewer_name": "reviewer1"
      }
    ]
  }
  ```

- **错误码**:
  | 状态码 | 描述 |
  |--------|------|
  | 401 | 无效的token |
  | 403 | 无权访问此接口 |

#### 4.7 获取系统统计信息
- **URL**: `/admin/statistics`
- **方法**: `GET`
- **请求参数**:
  | 参数名 | 类型 | 必填 | 描述 |
  |--------|------|------|------|
  | token | string | 是 | 登录凭证 |

- **响应示例**:
  ```json
  {
    "total_users": 100,
    "user_roles": [
      {"role": "user", "count": 80},
      {"role": "reviewer", "count": 15},
      {"role": "admin", "count": 5}
    ],
    "total_journals": 50,
    "journal_status": [
      {"status": "pending", "count": 20},
      {"status": "approved", "count": 25},
      {"status": "rejected", "count": 5}
    ],
    "total_reviews": 30
  }
  ```

- **错误码**:
  | 状态码 | 描述 |
  |--------|------|
  | 401 | 无效的token |
  | 403 | 无权访问此接口 |

## 通用错误码

| 状态码 | 描述 |
|--------|------|
| 400 | 请求参数错误 |
| 401 | 未授权（无效的token） |
| 403 | 禁止访问（权限不足） |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |
| 429 | 请求频率过高 |

## 文献状态说明

| 状态值 | 描述 |
|--------|------|
| pending | 待审核 |
| approved | 审核通过 |
| rejected | 审核拒绝 |

## 用户角色说明

| 角色值 | 描述 |
|--------|------|
| user | 普通用户 |
| reviewer | 审稿人 |
| admin | 管理员 |
