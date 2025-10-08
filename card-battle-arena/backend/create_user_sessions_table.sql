-- 创建user_sessions表的SQL脚本
-- 这个脚本直接解决user_sessions表缺失的问题

-- 创建user_sessions表
CREATE TABLE IF NOT EXISTS user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    refresh_token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    last_used_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    is_active BOOLEAN DEFAULT TRUE NOT NULL
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_user_sessions_last_used ON user_sessions(last_used_at);
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_token ON user_sessions(user_id, session_token);
CREATE INDEX IF NOT EXISTS idx_user_sessions_refresh_token ON user_sessions(refresh_token);

-- 插入Alembic版本记录（如果不存在）
CREATE TABLE IF NOT EXISTS alembic_version (
    version_num VARCHAR(32) PRIMARY KEY
);

INSERT INTO alembic_version (version_num)
VALUES ('001')
ON CONFLICT (version_num) DO NOTHING;

-- 验证表创建成功
SELECT
    'user_sessions' as table_name,
    COUNT(*) as record_count
FROM user_sessions;

-- 显示成功消息
DO $$
BEGIN
    RAISE NOTICE '✅ user_sessions表创建成功！';
    RAISE NOTICE '🎉 数据库表结构问题已解决';
    RAISE NOTICE '🚀 现在可以尝试登录功能了';
END $$;