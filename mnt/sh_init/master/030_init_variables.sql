USE `main`;
CREATE TABLE `users_status`
(
    `id`                BIGINT          NOT NULL    PRIMARY KEY     AUTO_INCREMENT,
    `name`              VARCHAR(40),
    `status`            TINYINT         NOT NULL    DEFAULT 1,
    `created_at`        DATETIME        NOT NULL    DEFAULT CURRENT_TIMESTAMP,
    `updated_at`        DATETIME        NOT NULL    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `is_valid`          TINYINT         NOT NULL    DEFAULT 1
);

NSERT INTO employee (name) VALUES
("reimu.h"), ("marisa.k");
