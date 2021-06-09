#!/bin/sh

ROOT_USER=root
REP_USER=rep
GEN_USER=user

# modify root auth type
echo "ALTER USER ${ROOT_USER} IDENTIFIED WITH mysql_native_password BY '${MYSQL_ROOT_PASSWORD}';" | "${mysql[@]}"

# create replication user(without slave promote to master)
echo "CREATE USER ${REP_USER} IDENTIFIED WITH mysql_native_password BY '${MYSQL_REP_PASSWORD}';" | "${mysql[@]}"
echo "GRANT REPLICATION SLAVE ON *.* TO '${REP_USER}';" | "${mysql[@]}"

# create normal user
echo "CREATE USER ${GEN_USER} IDENTIFIED WITH mysql_native_password BY '${MYSQL_USER_PASSWORD}';" | "${mysql[@]}"
echo "GRANT SELECT,UPDATE,INSERT ON ${MYSQL_DATABASE}.* TO ${GEN_USER};" | "${mysql[@]}"
# case not auth database as select by normal user
# echo "GRANT INSERT ON db_xxx.* TO '${GEN_USER}';" | "${mysql[@]}"
