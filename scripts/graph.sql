
# Primary data types. For instance, accumulated Wh, current temperature.

CREATE TABLE `data_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tag` char(255) DEFAULT NULL, # AMQP message type
  `method` int(2) NULL,
  `cycle_max` double(40,10) DEFAULT NULL, # limit of cyclic value
  `unit` char(10) NOT NULL DEFAULT '',
  `value` double(40,10) DEFAULT NULL, # last raw value seen; required for aggregation
  `aux_value` double(40,10) DEFAULT NULL, # last raw value seen; required for aggregation
  `display_order` int(3) NOT NULL default 0,
  `display_name` char(50) NULL,
  `display_unit` char(10) NULL,
  `display_factor` double(40,10) NOT NULL default 1,
  `n_values` int(11) NOT NULL default 0,
  # NULL  newly created
  # zero  ignored
  # 1     ignored and to-be-deleted
  # 2     no special treatment
  # 3     accumulated
  # 4     cyclic
  PRIMARY KEY (`id`),
  UNIQUE INDEX `i_tag`(`tag`(100))
);

# Raw log from AMQP.
# Data are deleted as soon as they get aggregated to level 0.

CREATE TABLE `data_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `data_type` int(11) NOT NULL,
  `value` double(40,10) DEFAULT NULL, # raw value from AMQP, *not* the delta!
  `aux_value` double(40,10) DEFAULT NULL, # raw value from AMQP, *not* the delta!
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `data_type` (`data_type`,`timestamp`),
  KEY `timestamp` (`timestamp`),
  CONSTRAINT `data_log_ibfk_1` FOREIGN KEY (`data_type`) REFERENCES `data_type` (`id`)
);

# Aggregation descriptors.
# Level 0 collects raw data,
# level 1 ff. the level below that.

CREATE TABLE `data_agg_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `data_type` int(11) NOT NULL,
  `layer` tinyint(2) NOT NULL DEFAULT 0,
  `interval` int(11) NOT NULL,
  `max_age` int(11) NOT NULL, # seconds until
  `timestamp` timestamp NOT NULL default "2000-01-01", # of last processed record
  `last_id` int(11) NOT NULL default 0, # of last analyzed record (may no longer exist)
  PRIMARY KEY (`id`),
  UNIQUE KEY `data_type` (`data_type`, `layer`),
  CONSTRAINT `data_aggtype_type` FOREIGN KEY (`data_type`) REFERENCES `data_type` (`id`)
);

# Aggregate data.
# Data are deleted when they get aggregated to the next level and
# the max_age (in data_agg_type.max_age) has been reached.

CREATE TABLE `data_agg` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `data_agg_type` int(11) NOT NULL,
  `value` double(40,10) NOT NULL,
  `aux_value` double(40,10) DEFAULT NULL, # cycle: confidence
  `min_value` double(40,10) NOT NULL,
  `max_value` double(40,10) NOT NULL,
  `n_values` integer not null default 0,
  `tsc` integer not null,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP, # start of period
  PRIMARY KEY (`id`),
  UNIQUE KEY `data_agg_tsc` (`data_agg_type`,`tsc`),
  KEY `timestamp` (`timestamp`),
  CONSTRAINT `data_agg_type` FOREIGN KEY (`data_agg_type`) REFERENCES `data_agg_type` (`id`)
);

