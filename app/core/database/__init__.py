# -*- coding: utf-8 -*-
"""数据库模块"""

# 导出MariaDB相关（推荐使用）
from app.core.database.mariadb import (
    MariaDBPool,
    mariadb_pool,
)

# 导出MySQL相关（向后兼容）
from app.core.database.mysql import (
    MySQLPool,
    mysql_pool,
)

# 统一导出别名（推荐使用mariadb_pool）
db_pool = mariadb_pool
