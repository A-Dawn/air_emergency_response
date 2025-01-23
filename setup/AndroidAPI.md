# 应急响应平台 API 文档

## 概述
本API文档提供了应急响应平台的所有API端点。这些端点允许用户进行注册、登录、创建和获取应急预案、事件记录、安全检查记录以及用户信息。

## 基础URL
所有请求的基准URL为：
```
http://<82.157.133.200:22>:<port>
```


## 认证
大多数API端点需要通过JWT Token进行认证。JWT Token需要在请求头中通过`Authorization`字段传递，格式如下：
```
Authorization: Bearer <your_jwt_token>
```

## 错误处理
所有API响应都会包含一个状态码和一个JSON对象。如果请求失败，响应对象中会包含一个`message`字段，说明错误的原因。

## API 端点

### 1. 用户认证

#### 1.1 注册用户
**请求方法**: `POST`  
**路径**: `/auth/register`  
**请求体**:
```json
{
  "username": "string",
  "role_level": "integer"
}
```
**响应**:
- **成功**:
  ```json
  {
    "message": "用户注册成功!",
    "private_key": "string"
  }
  ```
- **失败**:
  ```json
  {
    "message": "用户已存在!"
  }
  ```

#### 1.2 登录用户
**请求方法**: `POST`  
**路径**: `/auth/login`  
**请求体**:
```json
{
  "username": "string"
}
```
**响应**:
- **成功**:
  ```json
  {
    "token": "string"
  }
  ```
- **失败**:
  ```json
  {
    "message": "用户不存在!"
  }
  ```

#### 1.3 刷新Token
**请求方法**: `POST`  
**路径**: `/auth/refresh_token`  
**请求头**:
```
Authorization: Bearer <your_jwt_token>
```
**响应**:
- **成功**:
  ```json
  {
    "token": "string"
  }
  ```
- **失败**:
  ```json
  {
    "message": "缺少Token!"
  }
  ```

### 2. 应急预案管理

#### 2.1 创建应急预案
**请求方法**: `POST`  
**路径**: `/emergency-plans`  
**请求头**:
```
Authorization: Bearer <your_jwt_token>
```
**请求体**:
```json
{
  "plan_details": "string",
  "version": "string",
  "status": "integer"
}
```
**响应**:
- **成功**:
  ```json
  {
    "message": "应急预案创建成功!"
  }
  ```
- **失败**:
  ```json
  {
    "message": "缺少Token!"
  }
  ```

#### 2.2 获取应急预案
**请求方法**: `GET`  
**路径**: `/emergency-plans/<plan_id>`  
**请求头**:
```
Authorization: Bearer <your_jwt_token>
```
**响应**:
- **成功**:
  ```json
  {
    "plan_id": "integer",
    "plan_details": "string",
    "version": "string",
    "status": "integer"
  }
  ```
- **失败**:
  ```json
  {
    "message": "应急预案不存在!"
  }
  ```

### 3. 事件管理

#### 3.1 创建事件记录
**请求方法**: `POST`  
**路径**: `/incidents`  
**请求头**:
```
Authorization: Bearer <your_jwt_token>
```
**请求体**:
```json
{
  "incident_info": "string",
  "process_status": "integer",
  "response_log": "string",
  "incident_level": "integer",
  "assigned_resources": "string"
}
```
**响应**:
- **成功**:
  ```json
  {
    "message": "事件记录创建成功!"
  }
  ```
- **失败**:
  ```json
  {
    "message": "缺少Token!"
  }
  ```

#### 3.2 获取事件记录
**请求方法**: `GET`  
**路径**: `/incidents/<incident_id>`  
**请求头**:
```
Authorization: Bearer <your_jwt_token>
```
**响应**:
- **成功**:
  ```json
  {
    "incident_id": "integer",
    "incident_info": "string",
    "process_status": "integer",
    "response_log": "string",
    "incident_level": "integer",
    "assigned_resources": "string",
    "update_time": "yyyy-mm-dd hh:mm:ss"
  }
  ```
- **失败**:
  ```json
  {
    "message": "事件记录不存在!"
  }
  ```

### 4. 安全检查管理

#### 4.1 创建安全检查记录
**请求方法**: `POST`  
**路径**: `/security-checks`  
**请求头**:
```
Authorization: Bearer <your_jwt_token>
```
**请求体**:
```json
{
  "check_record": "string",
  "issue_tracking": "string",
  "improvement_status": "integer",
  "evaluation_report": "string"
}
```
**响应**:
- **成功**:
  ```json
  {
    "message": "安全检查记录创建成功!"
  }
  ```
- **失败**:
  ```json
  {
    "message": "缺少Token!"
  }
  ```

#### 4.2 获取安全检查记录
**请求方法**: `GET`  
**路径**: `/security-checks/<check_id>`  
**请求头**:
```
Authorization: Bearer <your_jwt_token>
```
**响应**:
- **成功**:
  ```json
  {
    "check_id": "integer",
    "check_record": "string",
    "issue_tracking": "string",
    "improvement_status": "integer",
    "evaluation_report": "string"
  }
  ```
- **失败**:
  ```json
  {
    "message": "安全检查记录不存在!"
  }
  ```

### 5. 用户管理

#### 5.1 创建用户（需要超级管理员权限）
**请求方法**: `POST`  
**路径**: `/users`  
**请求头**:
```
Authorization: Bearer <your_jwt_token>
```
**请求体**:
```json
{
  "username": "string",
  "role_level": "integer"
}
```
**响应**:
- **成功**:
  ```json
  {
    "message": "用户注册成功!",
    "private_key": "string"
  }
  ```
- **失败**:
  ```json
  {
    "message": "权限不足!"
  }
  ```

#### 5.2 获取用户信息
**请求方法**: `GET`  
**路径**: `/users/<user_id>`  
**请求头**:
```
Authorization: Bearer <your_jwt_token>
```
**响应**:
- **成功**:
  ```json
  {
    "user_id": "integer",
    "username": "string",
    "role_level": "integer"
  }
  ```
- **失败**:
  ```json
  {
    "message": "用户不存在!"
  }
  ```

## 示例请求

### 示例1: 注册用户
**请求URL**:
```
POST http://localhost:5000/auth/register
```
**请求体**:
```json
{
  "username": "testuser",
  "role_level": 1
}
```
**响应**:
```json
{
  "message": "用户注册成功!",
  "private_key": "your_private_key"
}
```

### 示例2: 登录用户
**请求URL**:
```
POST http://localhost:5000/auth/login
```
**请求体**:
```json
{
  "username": "testuser"
}
```
**响应**:
```json
{
  "token": "your_jwt_token"
}
```

### 示例3: 创建应急预案
**请求URL**:
```
POST http://localhost:5000/emergency-plans
```
**请求头**:
```
Authorization: Bearer your_jwt_token
```
**请求体**:
```json
{
  "plan_details": "火灾应急预案",
  "version": "1.0",
  "status": 1
}
```
**响应**:
```json
{
  "message": "应急预案创建成功!"
}
```

### 示例4: 获取应急预案
**请求URL**:
```
GET http://localhost:5000/emergency-plans/1
```
**请求头**:
```
Authorization: Bearer your_jwt_token
```
**响应**:
```json
{
  "plan_id": 1,
  "plan_details": "火灾应急预案",
  "version": "1.0",
  "status": 1
}
```

---
