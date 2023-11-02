-- MariaDB dump 10.19  Distrib 10.4.28-MariaDB, for FreeBSD12.4 (amd64)
--
-- Host: localhost    Database: jupiter
-- ------------------------------------------------------
-- Server version	10.4.28-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

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
) ENGINE=InnoDB AUTO_INCREMENT=89791 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
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
  `devjson` longtext DEFAULT NULL CHECK (json_valid(`devjson`)),
  PRIMARY KEY (`id`),
  UNIQUE KEY `hostname` (`hostname`)
) ENGINE=InnoDB AUTO_INCREMENT=33743793 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
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
  `imgdata` mediumblob DEFAULT NULL,
  `imgdatalen` int(10) GENERATED ALWAYS AS (octet_length(`imgdata`)) STORED,
  UNIQUE KEY `idx_imgid_size` (`imgid`,`size`),
  KEY `idx_size` (`size`),
  KEY `idx_imgid` (`imgid`),
  KEY `imgidlookup` (`imgid`),
  CONSTRAINT `imgcache_ibfk_1` FOREIGN KEY (`imgid`) REFERENCES `thumblist` (`imgid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `lightschedule`
--

DROP TABLE IF EXISTS `lightschedule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `lightschedule` (
  `hhcode` varchar(1) NOT NULL DEFAULT 'I',
  `lightcode` int(2) NOT NULL,
  `monthmatch` varchar(20) NOT NULL,
  `daymatch` varchar(20) NOT NULL,
  `turnon` varchar(20) NOT NULL,
  `turnoff` varchar(20) NOT NULL,
  `id` int(16) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`hhcode`,`lightcode`,`monthmatch`,`daymatch`,`turnon`,`turnoff`),
  UNIQUE KEY `id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=92 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
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
) ENGINE=InnoDB AUTO_INCREMENT=77537 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
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
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
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
) ENGINE=InnoDB AUTO_INCREMENT=147745 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-11-01 13:55:43
