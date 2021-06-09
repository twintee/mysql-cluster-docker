USE `main`;
CREATE TABLE `c_users_status`
(
    `status`            TINYINT         NOT NULL    PRIMARY KEY     AUTO_INCREMENT,
    `name`              VARCHAR(40),
    `created_at`        DATETIME        NOT NULL    DEFAULT CURRENT_TIMESTAMP,
    `updated_at`        DATETIME        NOT NULL    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `is_valid`          TINYINT         NOT NULL    DEFAULT 1
);
