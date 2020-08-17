



DROP TABLE IF EXISTS `stock_info`;

CREATE TABLE `stock_info` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'stock id',
  `symbol` varchar(30) NOT NULL DEFAULT '' COMMENT '股票代码',
  `trade_date` varchar(20) NOT NULL DEFAULT '' COMMENT '交易日期',
  `name` varchar(30) NOT NULL DEFAULT '' COMMENT '公司名称',
  `open` float  COMMENT '开盘价',
  `close` float  COMMENT '收盘价',
  `high` float  COMMENT '最高价',
  `low` float  COMMENT '最低价',
  `vol` float  COMMENT '交易量',
  PRIMARY KEY (`id`),
  UNIQUE KEY `SYMBOL_TRADE_DATE` (`symbol`,`trade_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票信息';

create table `cursor_date`(
    `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'stock id',
    `cursor_date` varchar(20) NOT NULL DEFAULT '' COMMENT 'cursor date',
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='cursor date';

// run on liux:
flask-sqlacodegen 'mysql://root:123321@192.168.123.169/stock_ai' --tables cursor_date --outfile "common/models/cursor_date.py"  --flas



CREATE TABLE `result`(
 `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'result id',
 `symbol` varchar(20) NOT NULL DEFAULT '' COMMENT '选股结果',
 `date` varchar(20) NOT NULL DEFAULT '' COMMENT '选股日期',
 `price` float NOT NULL DEFAULT 0 COMMENT '买入价格',
 PRIMARY KEY (`id`),
 UNIQUE KEY `SYMBOL_DATE` (`symbol`,`date`)
 ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='选股结果表';


CREATE TABLE `stock_list`(
     `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'id',
     `symbol` varchar(20) NOT NULL DEFAULT '' COMMENT 'symbol',
     PRIMARY KEY (`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票列表';

mysql -h sotckai.c8ut9axdtyf4.us-east-1.rds.amazonaws.com -u root -p

CREATE TABLE `user_info` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'id',
  `hold_stock` varchar(20) NOT NULL DEFAULT '' COMMENT '持有股票代码',
  `user_id` bigint(20) NOT NULL DEFAULT 0 COMMENT '用户id fk',
  `buy_price` float NOT NULL DEFAULT 0 COMMENT '卖出价格',
  `sold_price` float  COMMENT '卖出价格',
  `strategy` varchar(2000)  COMMENT '当前交易策略',
  `buy_date` varchar(20)  COMMENT '买入日期',
  `sale_date` float  COMMENT '卖出日期',
  PRIMARY KEY (`id`),
  FOREIGN KEY (`user_id`) REFERENCES user(uid),
  UNIQUE KEY `USER_STOCK_DATE` (`user_id`,`hold_stock`,`buy_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户交易信息';



CREATE TABLE `notify` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'id',
  `symbol` varchar(20) NOT NULL DEFAULT '' COMMENT '持有股票代码',
  `date` varchar(20) NOT NULL DEFAULT '' COMMENT '交易日期',
  `user_id` bigint(20) NOT NULL DEFAULT 0 COMMENT '用户id fk',
  PRIMARY KEY (`id`),
  FOREIGN KEY (`user_id`) REFERENCES user(uid),
  UNIQUE KEY `SYMBOL_DATE_UID` (`symbol`,`date`,`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='提醒信息';


CREATE TABLE `transaction_history`(
 `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'history id',
 `uid` bigint(20) NOT NULL  COMMENT '用户id',
 `date` varchar(20) NOT NULL DEFAULT '' COMMENT '选出日期',
 `name` varchar(20) NOT NULL DEFAULT '' COMMENT '股票名称',
 `symbol` varchar(20) NOT NULL DEFAULT '' COMMENT '股票代码',
 `hold_time` varchar(2) NOT NULL DEFAULT '' COMMENT '持有时间',
 `status` varchar(20) NOT NULL DEFAULT '持有' COMMENT '状态',
 PRIMARY KEY (`id`),
 UNIQUE KEY `DATE_SYMBOL` (`symbol`,`date`)
 ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='选股历史表';

 DROP TABLE IF EXISTS `gold_cross_result`;

 CREATE TABLE `gold_cross_result`(
 `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'result id',
 `symbol` varchar(20) NOT NULL DEFAULT '' COMMENT '选股结果',
 `name` varchar(20) NOT NULL DEFAULT '' COMMENT '选股名称',
 `date` varchar(20) NOT NULL DEFAULT '' COMMENT '选股日期',
 `price` float NOT NULL DEFAULT 0 COMMENT '买入价格',
 PRIMARY KEY (`id`),
 UNIQUE KEY `SYMBOL_DATE` (`symbol`,`date`)
 ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='选股结果表';

  DROP TABLE IF EXISTS `nh_result`;
  CREATE TABLE `nh_result`(
 `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'result id',
 `symbol` varchar(20) NOT NULL DEFAULT '' COMMENT '选股结果',
 `name` varchar(20) NOT NULL DEFAULT '' COMMENT '选股名称',
 `date` varchar(20) NOT NULL DEFAULT '' COMMENT '选股日期',
 `price` float NOT NULL DEFAULT 0 COMMENT '买入价格',
 PRIMARY KEY (`id`),
 UNIQUE KEY `SYMBOL_DATE` (`symbol`,`date`)
 ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='选股结果表';

 DROP TABLE IF EXISTS `second_up_result`;
 CREATE TABLE `second_up_result`(
 `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'result id',
 `symbol` varchar(20) NOT NULL DEFAULT '' COMMENT '选股结果',
 `name` varchar(20) NOT NULL DEFAULT '' COMMENT '选股名称',
 `date` varchar(20) NOT NULL DEFAULT '' COMMENT '选股日期',
 `price` float NOT NULL DEFAULT 0 COMMENT '买入价格',
 PRIMARY KEY (`id`),
 UNIQUE KEY `SYMBOL_DATE` (`symbol`,`date`)
 ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='选股结果表';

 DROP TABLE IF EXISTS `user_info`;
 CREATE TABLE `user_info` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'id',
  `hold_stock` varchar(20) NOT NULL DEFAULT '' COMMENT '持有股票代码',
  `name` varchar(20) NOT NULL DEFAULT '' COMMENT '股票名称',
  `user_id` bigint(20) NOT NULL DEFAULT 0 COMMENT '用户id fk',
  `buy_price` float NOT NULL DEFAULT 0 COMMENT '卖出价格',
  `sold_price` float  COMMENT '卖出价格',
  `strategy` varchar(2000)  COMMENT '当前交易策略',
  `buy_date` varchar(20)  COMMENT '买入日期',
  `hold_time` float  COMMENT '卖出日期',
  PRIMARY KEY (`id`),
  FOREIGN KEY (`user_id`) REFERENCES user(uid),
  UNIQUE KEY `USER_STOCK_DATE` (`user_id`,`hold_stock`,`buy_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户交易信息';