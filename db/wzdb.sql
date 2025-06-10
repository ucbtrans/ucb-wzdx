-- MySQL dump 10.13  Distrib 8.0.18, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: wzdb
-- ------------------------------------------------------
-- Server version	5.7.40-0ubuntu0.18.04.1

SET foreign_key_checks = 0;

--
-- Table structure for table `lane`
--

DROP TABLE IF EXISTS `lane`;
CREATE TABLE `lane` (
  `road_event_feature_id` varchar(64) NOT NULL COMMENT 'Reference to the PK of the table road_event_feature',
  `order` int(11) NOT NULL DEFAULT 1 COMMENT 'The position of a lane in sequence on the roadway. This value is used as an index to indicate the order of all lanes provided for a road event, starting with 1 for the left-most lane.',
  `type` varchar(45) NOT NULL DEFAULT 'general' COMMENT 'An indication of the type of lane or shoulder. Values: general, exit-lane, exit-ramp, entrance-lane, entrance-ramp, sidewalk, bike-lane, shoulder, parking, median, two-way-center-turn-lane.',
  `status` varchar(45) NOT NULL DEFAULT 'closed' COMMENT 'Status of the lane for the traveling public. Values: open, closed, shift-left, shift-right, merge-left, merge-right, alternating-flow.',
  KEY `id4` (`road_event_feature_id`),
  CONSTRAINT `id4` FOREIGN KEY (`road_event_feature_id`) REFERENCES `road_event_feature` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Lane information.';


--
-- Table structure for table `related_road_event`
--

DROP TABLE IF EXISTS `related_road_event`;
CREATE TABLE `related_road_event` (
  `road_event_feature_id` varchar(64) NOT NULL COMMENT 'Reference to the PK of the table road_event_feature',
  `related_event_id` varchar(64) NOT NULL COMMENT 'Reference to the PK of the table road_event_feature',
  KEY `id6_idx` (`road_event_feature_id`),
  KEY `id7_idx` (`related_event_id`),
  CONSTRAINT `id6` FOREIGN KEY (`road_event_feature_id`) REFERENCES `road_event_feature` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION,
  CONSTRAINT `id7` FOREIGN KEY (`related_event_id`) REFERENCES `road_event_feature` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='List of related events.';


--
-- Table structure for table `restrictions`
--

DROP TABLE IF EXISTS `restrictions`;
CREATE TABLE `restrictions` (
  `road_event_feature_id` varchar(64) NOT NULL COMMENT 'Reference to the PK of the table road_event_feature',
  `lane_order` int(11) DEFAULT NULL COMMENT 'Lane order. If null, the restriction applies to the whole WZ.',
  `type` varchar(45) NOT NULL DEFAULT 'no-parking' COMMENT 'The type of restriction being enforced. Values: local-access-only, no-trucks, travel-peak-hours-only, hov-3, hov-2, no-parking, reduced-width, reduced-height, reduced-length, reduced-weight, axle-load-limit, gross-weight-limit, towing-prohibited, permitted-oversize-loads-prohibited, no-passing',
  `value` int(11) DEFAULT NULL COMMENT 'A value associated with the restriction, if applicable',
  `unit` varchar(45) DEFAULT NULL COMMENT 'Unit of measurement for the restriction value, if applicable. Values: feet, inches, centimeters, pounds, tons, kilograms.',
  KEY `id3_idx` (`road_event_feature_id`),
  CONSTRAINT `id3` FOREIGN KEY (`road_event_feature_id`) REFERENCES `road_event_feature` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Restrictions applied to WZs.';


--
-- Table structure for table `road_event_core_details`
--

DROP TABLE IF EXISTS `road_event_core_details`;
CREATE TABLE `road_event_core_details` (
  `road_event_feature_id` varchar(64) NOT NULL COMMENT 'Reference to the PK of the table road_event_feature',
  `event_type` varchar(45) NOT NULL COMMENT 'The type/classification of road event. Values: work-zone, detour.',
  `data_source_id` varchar(45) NOT NULL COMMENT 'Identifies the data source from which the road event originates.',
  `road_names` varchar(256) NOT NULL COMMENT 'A list of publicly known names of the road on which the event occurs. This may include the road number designated by a jurisdiction such as a county, state or interstate (e.g. I-5, VT 133). Multiple values should be comma-separated.',
  `direction` varchar(45) NOT NULL DEFAULT 'unknown' COMMENT 'The digitization direction of the road that is impacted by the event. This value is based on the standard naming for US roadways and indicates the direction of the traffic flow regardless of the real heading angle. Values: northbound, eastbound, southbound, westbound, inner-loop, outer-loop, undefined, unknown.',
  `name` varchar(64) DEFAULT NULL COMMENT 'A human-readable name for the road event',
  `description` varchar(256) DEFAULT NULL COMMENT 'Short free text description of road event',
  `creation_date` datetime DEFAULT NULL COMMENT 'The UTC time and date when the activity or event was created',
  `update_date` datetime DEFAULT NULL COMMENT 'The UTC date and time when any information for this road_event_feature_id (including child objects) that the RoadEventCoreDetails applies to was most recently updated or confirmed as up to date.',
  KEY `id8_idx` (`road_event_feature_id`),
  CONSTRAINT `id8` FOREIGN KEY (`road_event_feature_id`) REFERENCES `road_event_feature` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Core information about the road events.';


--
-- Table structure for table `road_event_feature`
--

DROP TABLE IF EXISTS `road_event_feature`;
CREATE TABLE `road_event_feature` (
  `id` varchar(64) NOT NULL,
  `geometry` geometry NOT NULL COMMENT 'The geometry of the road event. The Geometry object''s type property MUST be LineString or MultiPoint. LineString allows specifying the entire road event path and should be preferred. MultiPoint should be used when only the start and end coordinates are known. The order of coordinates is meaningful: the first coordinate is the first (furthest upstream) point a road user encounters when traveling through the road event. If a data producer has three or more coordinates that are on the road event path, a LineString geometry should be used because it indicates that the points are ordered.',
  `deleted` datetime DEFAULT NULL COMMENT 'DATETIME flag indicating when the event was deleted',
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  SPATIAL KEY `g_SPATIAL` (`geometry`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Main table - event IDs and geometries.';


--
-- Table structure for table `type_of_work`
--

DROP TABLE IF EXISTS `type_of_work`;
CREATE TABLE `type_of_work` (
  `road_event_feature_id` varchar(64) NOT NULL COMMENT 'Reference to the PK of the table road_event_feature',
  `type_name` varchar(45) NOT NULL DEFAULT 'maintenance' COMMENT 'A high-level text description of the type of work being done. Values: maintenance, minor-road-defect-repair, roadside-work, overhead-work, below-road-work, barrier-work, surface-work, painting, roadway-relocation, roadway-creation',
  `is_architectural_change` tinyint(4) DEFAULT NULL COMMENT 'A flag indicating whether the type of work will result in an architectural change to the roadway',
  KEY `id2` (`road_event_feature_id`),
  CONSTRAINT `id2` FOREIGN KEY (`road_event_feature_id`) REFERENCES `road_event_feature` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


--
-- Table structure for table `work_zone_event`
--

DROP TABLE IF EXISTS `work_zone_event`;
CREATE TABLE `work_zone_event` (
  `road_event_feature_id` varchar(64) NOT NULL COMMENT 'Reference to the PK of the table road_event_feature',
  `start_date` datetime NOT NULL COMMENT 'The UTC time and date when the event begins',
  `end_date` datetime NOT NULL COMMENT 'The UTC time and date when the event ends',
  `is_start_date_verified` tinyint(4) DEFAULT NULL COMMENT 'Indicates if work has been confirmed to have started, such as from a person or field device',
  `is_end_date_verified` tinyint(4) DEFAULT NULL COMMENT 'Indicates if work has been confirmed to have ended, such as from a person or field device',
  `is_start_position_verified` tinyint(4) DEFAULT NULL COMMENT 'Indicates if the start position (first geometric coordinate pair) is based on actual reported data from a GPS-equipped device that measured the location of the start of the work zone',
  `is_end_position_verified` tinyint(4) DEFAULT NULL COMMENT 'Indicates if the end position (last geometric coordinate pair) is based on actual reported data from a GPS-equipped device that measured the location of the end of the work zone',
  `work_zone_type` varchar(45) DEFAULT NULL COMMENT 'The type of work zone road event, such as if the road event is static or actively moving as part of a moving operation. Values: static, moving, planned-moving-area',
  `location_method` varchar(45) NOT NULL DEFAULT 'unknown' COMMENT 'The typical method used to locate the beginning and end of a work zone impact area. Values: channel-device-method, sign-method, junction-method, other, unknown',
  `vehicle_impact` varchar(45) NOT NULL DEFAULT 'unknown' COMMENT 'The impact to vehicular lanes along a single road in a single direction. Values: all-lanes-closed, some-lanes-closed, all-lanes-open, alternating-one-way, some-lanes-closed-merge-left, some-lanes-closed-merge-right, all-lanes-open-shift-left, all-lanes-open-shift-right, some-lanes-closed-split, flagging, temporary-traffic-signal, unknown',
  `beginning_cross_street` varchar(64) DEFAULT NULL COMMENT 'Name or number of the nearest cross street along the roadway where the event begins',
  `ending_cross_street` varchar(64) DEFAULT Null COMMENT 'Name or number of the nearest cross street along the roadway where the event ends',
  `beginning_milepost` decimal(6,2) DEFAULT NULL COMMENT 'The linear distance measured against a milepost marker along a roadway where the event begins',
  `ending_milepost` decimal(6,2) DEFAULT NULL COMMENT 'The linear distance measured against a milepost marker along a roadway where the event ends',
  `reduced_speed_limit_kph` int(11) DEFAULT NULL COMMENT 'The reduced speed limit posted within the road event, in kilometers per hour',
  KEY `id_idx` (`road_event_feature_id`),
  CONSTRAINT `id` FOREIGN KEY (`road_event_feature_id`) REFERENCES `road_event_feature` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='WZ description.';


--
-- Table structure for table `worker_presence`
--

DROP TABLE IF EXISTS `worker_presence`;
CREATE TABLE `worker_presence` (
  `road_event_feature_id` varchar(64) NOT NULL COMMENT 'Reference to the PK of the table road_event_feature',
  `are_workers_present` tinyint(4) NOT NULL DEFAULT '1' COMMENT 'Whether workers are present in the work zone event area. This value should be set in accordance with the definition provided in the definition property if it is provided.',
  `definition` varchar(512) DEFAULT NULL COMMENT 'A list of situations in which workers are considered to be present in the jurisdiction of the data provider. Multiple values (comma-separated) are allowed. Values: workers-in-work-zone-working, workers-in-work-zone-not-working, mobile-equipment-in-work-zone-moving, mobile-equipment-in-work-zone-not-moving, fixed-equipment-in-work-zone, humans-behind-barrier, humans-in-right-of-way.',
  `method` varchar(45) DEFAULT 'scheduled' COMMENT 'Describes the method for how worker presence in a work zone event area is determined. Values: camera-monitoring, arrow-board-present, cones-present, maintenance-vehicle-present, wearables-present, mobile-device-present, check-in-app, check-in-verbal, scheduled.',
  `worker_presence_last_confirmed_date` datetime DEFAULT NULL COMMENT 'The UTC date and time at which the presence of workers was last confirmed.',
  `confidence` varchar(45) DEFAULT 'low' COMMENT 'The data producer’s confidence in the value of are_workers_present. Values: low, medium, high.',
  KEY `id5_idx` (`road_event_feature_id`),
  CONSTRAINT `id5` FOREIGN KEY (`road_event_feature_id`) REFERENCES `road_event_feature` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COMMENT='Information about the presence of workers in the WZ.';



SET foreign_key_checks = 1;
