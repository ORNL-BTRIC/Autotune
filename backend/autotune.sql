-- phpMyAdmin SQL Dump
-- version 3.5.2.2
-- http://www.phpmyadmin.net
--
-- Host: 127.0.0.1
-- Generation Time: May 13, 2013 at 04:38 PM
-- Server version: 5.5.27
-- PHP Version: 5.4.7

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `autotune`
--

-- --------------------------------------------------------

--
-- Table structure for table `model`
--

CREATE TABLE IF NOT EXISTS `model` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `file` mediumblob,
  `fit` double DEFAULT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=181 ;


--
-- Table structure for table `tracking`
--

CREATE TABLE IF NOT EXISTS `tracking` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `queuePosition` int(10) NOT NULL,
  `terminate` tinyint(1) NOT NULL DEFAULT '0',
  `baseModel` mediumblob,
  `parameters` mediumblob,
  `schedule` longblob,
  `userData` longblob,
  `weather` varchar(80) DEFAULT NULL,
  `email` varchar(60) DEFAULT NULL,
  `runtime` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=3 ;


--
-- Table structure for table `trackingmodel`
--

CREATE TABLE IF NOT EXISTS `trackingmodel` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `trackingId` bigint(20) NOT NULL,
  `modelId` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `TrackingModel_Tracking_FK` (`trackingId`),
  KEY `TrackingModel_Model_FK` (`modelId`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=181 ;


--
-- Constraints for dumped tables
--

--
-- Constraints for table `trackingmodel`
--
ALTER TABLE `trackingmodel`
  ADD CONSTRAINT `TrackingModel_Model_FK` FOREIGN KEY (`modelId`) REFERENCES `model` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `TrackingModel_Tracking_FK` FOREIGN KEY (`trackingId`) REFERENCES `tracking` (`id`) ON DELETE CASCADE;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
