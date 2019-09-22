-- MySQL dump 10.13  Distrib 5.7.27, for FreeBSD11.2 (amd64)
--
-- Host: *db_host*    Database: *db_name*
-- ------------------------------------------------------
-- Server version	5.7.26-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
SET @MYSQLDUMP_TEMP_LOG_BIN = @@SESSION.SQL_LOG_BIN;
SET @@SESSION.SQL_LOG_BIN= 0;

--
-- GTID state at the beginning of the backup 
--

SET @@GLOBAL.GTID_PURGED='2a2c8a5f-a03f-11e6-aaf5-001f294224d2:1-485,
aa282831-a96a-11e6-b5e7-001f294224d2:1-1036857,
b96b2a5f-c956-11e5-ae6b-001f294224d2:1-5072';

--
-- Table structure for table `crosslinks`
--

DROP TABLE IF EXISTS `crosslinks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `crosslinks` (
  `fileid` int(12) NOT NULL AUTO_INCREMENT,
  `fname` varchar(512) NOT NULL,
  `inode` int(12) DEFAULT NULL,
  `size` int(20) DEFAULT NULL,
  `md5` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`fileid`),
  UNIQUE KEY `crosslinks_fname` (`fname`),
  KEY `crosslinks_md5` (`md5`),
  KEY `crosslinks_size` (`size`),
  KEY `crosslinks_inode` (`inode`)
) ENGINE=InnoDB AUTO_INCREMENT=89791 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `devices`
--

DROP TABLE IF EXISTS `devices`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `devices` (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `hostname` varchar(128) NOT NULL,
  `devjson` json DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `hostname` (`hostname`)
) ENGINE=InnoDB AUTO_INCREMENT=3617400 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `imgcache`
--

DROP TABLE IF EXISTS `imgcache`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `imgcache` (
  `imgid` int(16) NOT NULL,
  `size` varchar(32) NOT NULL,
  `imgdata` mediumblob,
  `imgdatalen` int(10) GENERATED ALWAYS AS (length(`imgdata`)) STORED,
  UNIQUE KEY `idx_imgid_size` (`imgid`,`size`),
  KEY `idx_size` (`size`),
  KEY `idx_imgid` (`imgid`),
  KEY `imgidlookup` (`imgid`),
  CONSTRAINT `imgcache_ibfk_1` FOREIGN KEY (`imgid`) REFERENCES `thumblist` (`imgid`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `musicfiles`
--

DROP TABLE IF EXISTS `musicfiles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `musicfiles` (
  `filename` varchar(512) NOT NULL,
  `fileid` int(12) NOT NULL AUTO_INCREMENT,
  `shortname` varchar(256) NOT NULL,
  `inode` int(12) DEFAULT NULL,
  `checksum` char(32) DEFAULT NULL,
  `size` int(16) DEFAULT NULL,
  PRIMARY KEY (`fileid`),
  UNIQUE KEY `musicfiles_filename` (`filename`) USING BTREE,
  UNIQUE KEY `filename` (`filename`),
  UNIQUE KEY `filename_2` (`filename`),
  KEY `musicfiles_inode` (`inode`),
  KEY `musicfiles_size` (`size`),
  KEY `musicfiles_checksum` (`checksum`)
) ENGINE=InnoDB AUTO_INCREMENT=77537 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `playlist`
--

DROP TABLE IF EXISTS `playlist`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `playlist` (
  `fileid` int(12) NOT NULL,
  `timestamp` int(12) DEFAULT NULL,
  UNIQUE KEY `fileid` (`fileid`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `thumblist`
--

DROP TABLE IF EXISTS `thumblist`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `thumblist` (
  `urr` int(11) DEFAULT NULL,
  `urg` int(11) DEFAULT NULL,
  `urb` int(11) DEFAULT NULL,
  `ulr` int(11) DEFAULT NULL,
  `ulg` int(11) DEFAULT NULL,
  `ulb` int(11) DEFAULT NULL,
  `lrr` int(11) DEFAULT NULL,
  `lrg` int(11) DEFAULT NULL,
  `lrb` int(11) DEFAULT NULL,
  `llr` int(11) DEFAULT NULL,
  `llg` int(11) DEFAULT NULL,
  `llb` int(11) DEFAULT NULL,
  `fname` varchar(512) NOT NULL,
  `imgid` int(16) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`imgid`),
  UNIQUE KEY `thumblist_fname` (`fname`)
) ENGINE=InnoDB AUTO_INCREMENT=134700 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
SET @@SESSION.SQL_LOG_BIN = @MYSQLDUMP_TEMP_LOG_BIN;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2019-09-21 15:07:07
