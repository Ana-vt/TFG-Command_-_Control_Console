-- MySQL dump 10.13  Distrib 8.0.23, for Win64 (x86_64)
--
-- Host: localhost    Database: flask_usuarios
-- ------------------------------------------------------
-- Server version	8.0.23

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `actions`
--

DROP TABLE IF EXISTS `actions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `actions` (
  `idactions` int NOT NULL AUTO_INCREMENT,
  `title` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`idactions`),
  UNIQUE KEY `idactions_UNIQUE` (`idactions`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `actions`
--

LOCK TABLES `actions` WRITE;
/*!40000 ALTER TABLE `actions` DISABLE KEYS */;
INSERT INTO `actions` VALUES (1,'pandora'),(2,'registro'),(3,'login');
/*!40000 ALTER TABLE `actions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sensores`
--

DROP TABLE IF EXISTS `sensores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sensores` (
  `idsensores` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(255) NOT NULL,
  `tipo` varchar(255) NOT NULL,
  `mac` char(17) DEFAULT NULL,
  `ip` varchar(39) DEFAULT NULL,
  `descripcion` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`idsensores`),
  UNIQUE KEY `idsensores_UNIQUE` (`idsensores`),
  UNIQUE KEY `nombre_UNIQUE` (`nombre`),
  UNIQUE KEY `mac_UNIQUE` (`mac`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sensores`
--

LOCK TABLES `sensores` WRITE;
/*!40000 ALTER TABLE `sensores` DISABLE KEYS */;
INSERT INTO `sensores` VALUES (1,'SENSOR_PLIVS_RM','Bluetooth','0987654333','372349843334','desplegados'),(2,'SENSOR_PLICA_BLUETOOTH','Bluetooth','09:7u:6y:5g:5f','145.65.78.10','sensor de prueba'),(14,'Redes Móviles','Bluetooth','23456710','19289765','v2.0');
/*!40000 ALTER TABLE `sensores` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_actions`
--

DROP TABLE IF EXISTS `user_actions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_actions` (
  `id_user` int NOT NULL,
  `action` int NOT NULL,
  `timestamp` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_user`,`action`,`timestamp`),
  KEY `fk_actionid_idx` (`action`),
  CONSTRAINT `fk_action` FOREIGN KEY (`action`) REFERENCES `actions` (`idactions`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_user` FOREIGN KEY (`id_user`) REFERENCES `usuarios` (`iduser`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_actions`
--

LOCK TABLES `user_actions` WRITE;
/*!40000 ALTER TABLE `user_actions` DISABLE KEYS */;
INSERT INTO `user_actions` VALUES (1,1,'2021-05-22 12:20:51'),(1,1,'2021-05-22 12:22:24'),(1,1,'2021-05-22 12:24:13'),(1,1,'2021-05-22 12:24:16'),(1,1,'2021-05-22 12:24:20'),(1,1,'2021-05-22 12:24:58'),(1,1,'2021-05-22 12:25:21'),(1,1,'2021-05-22 12:34:55'),(1,1,'2021-05-22 12:34:58'),(1,1,'2021-05-26 12:25:39'),(1,1,'2021-05-26 12:26:21'),(1,1,'2021-05-26 12:42:15'),(1,1,'2021-05-26 12:43:29'),(1,1,'2021-05-26 12:46:18'),(1,1,'2021-05-26 12:47:37'),(1,1,'2021-05-26 13:33:37'),(1,1,'2021-06-01 10:20:14'),(1,1,'2021-06-01 10:30:46'),(1,1,'2021-06-01 10:44:43'),(1,1,'2021-06-01 10:45:10'),(1,1,'2021-06-01 10:45:19'),(1,1,'2021-06-01 10:46:22'),(1,1,'2021-06-01 10:46:31'),(1,1,'2021-06-01 10:47:18'),(1,1,'2021-06-01 10:50:28'),(1,1,'2021-06-01 10:50:34'),(1,1,'2021-06-01 10:50:42'),(1,1,'2021-06-01 10:50:59'),(1,1,'2021-06-01 11:09:04'),(1,1,'2021-06-01 11:52:10'),(1,1,'2021-06-01 11:53:20'),(1,1,'2021-06-01 11:55:58'),(1,1,'2021-06-01 12:09:26'),(1,1,'2021-06-01 12:12:20'),(1,1,'2021-06-01 12:13:02'),(1,1,'2021-06-01 12:13:47'),(1,1,'2021-06-01 12:19:43'),(1,1,'2021-06-01 12:24:06'),(1,1,'2021-06-01 12:27:41'),(1,1,'2021-06-01 13:00:27'),(1,1,'2021-06-01 13:00:48'),(1,1,'2021-06-01 13:00:56'),(1,1,'2021-06-01 13:01:00'),(1,1,'2021-06-01 16:07:27'),(1,1,'2021-06-01 16:08:15'),(1,1,'2021-06-01 16:08:26'),(1,1,'2021-06-01 16:08:40'),(1,1,'2021-06-01 16:09:51'),(1,1,'2021-06-01 16:11:00'),(1,1,'2021-06-01 16:11:36'),(1,1,'2021-06-01 16:13:10'),(1,1,'2021-06-01 16:15:22'),(1,1,'2021-06-01 16:15:38'),(1,1,'2021-06-01 16:17:17'),(1,1,'2021-06-01 16:17:22'),(1,1,'2021-06-01 16:17:25'),(1,1,'2021-06-01 16:17:28'),(1,1,'2021-06-01 16:21:09'),(1,1,'2021-06-01 16:21:14'),(1,1,'2021-06-01 16:22:05'),(1,1,'2021-06-01 16:22:09'),(1,1,'2021-06-01 16:22:12'),(1,1,'2021-06-01 16:33:22'),(1,1,'2021-06-01 16:33:25'),(1,1,'2021-06-01 16:33:27'),(1,1,'2021-06-01 16:33:30'),(1,1,'2021-06-01 16:37:18'),(1,1,'2021-06-01 16:37:31'),(1,1,'2021-06-01 16:37:47'),(1,1,'2021-06-01 16:37:59'),(1,1,'2021-06-01 16:38:03'),(1,1,'2021-06-01 16:39:20'),(1,1,'2021-06-01 16:39:23'),(1,1,'2021-06-01 16:39:25'),(1,1,'2021-06-01 16:39:28'),(1,1,'2021-06-02 10:08:25'),(1,1,'2021-06-09 16:25:49'),(1,1,'2021-06-09 16:26:02'),(1,1,'2021-06-09 16:26:05'),(1,1,'2021-06-09 16:26:08'),(1,1,'2021-06-12 16:10:43'),(1,1,'2021-06-12 17:15:45'),(1,1,'2021-06-13 10:16:01'),(1,1,'2021-06-13 10:16:46'),(1,1,'2021-06-13 10:17:31'),(1,1,'2021-06-13 10:17:41'),(1,1,'2021-06-13 10:18:28'),(1,1,'2021-06-13 20:08:54'),(1,1,'2021-06-13 20:09:13'),(1,1,'2021-06-13 20:09:15'),(1,1,'2021-06-13 20:09:18'),(1,1,'2021-06-13 20:15:28'),(1,1,'2021-06-13 20:15:32'),(1,1,'2021-06-13 20:15:35'),(1,1,'2021-06-13 20:15:39'),(1,1,'2021-06-13 20:17:09'),(1,1,'2021-06-13 20:17:12'),(1,1,'2021-06-13 20:17:15'),(1,1,'2021-06-13 20:17:18'),(1,1,'2021-06-13 20:20:40'),(1,1,'2021-06-13 20:21:01'),(1,1,'2021-06-17 11:09:27'),(3,1,'2021-06-13 20:56:04'),(3,1,'2021-06-13 20:59:27'),(3,1,'2021-06-13 20:59:42'),(3,1,'2021-06-13 21:00:16'),(3,1,'2021-06-13 21:30:31'),(3,1,'2021-06-13 21:30:33'),(3,1,'2021-06-13 21:30:36'),(3,1,'2021-06-13 21:30:40'),(3,1,'2021-06-13 21:36:14'),(3,1,'2021-06-13 21:37:00'),(3,1,'2021-06-17 12:09:33'),(27,2,'2021-05-20 19:36:04'),(30,2,'2021-05-22 11:24:58'),(1,3,'2021-05-09 10:38:09'),(1,3,'2021-05-09 10:39:32'),(1,3,'2021-05-09 11:16:00'),(1,3,'2021-05-09 12:03:00'),(1,3,'2021-05-10 09:57:12'),(1,3,'2021-05-10 17:00:52'),(1,3,'2021-05-10 17:12:17'),(1,3,'2021-05-13 10:02:17'),(1,3,'2021-05-16 11:53:38'),(1,3,'2021-05-20 12:10:27'),(1,3,'2021-05-20 19:35:37'),(1,3,'2021-05-21 09:57:43'),(1,3,'2021-05-21 10:05:55'),(1,3,'2021-05-22 10:37:52'),(1,3,'2021-05-26 12:25:00'),(1,3,'2021-06-01 10:18:42'),(1,3,'2021-06-01 10:44:37'),(1,3,'2021-06-01 10:47:11'),(1,3,'2021-06-01 12:24:02'),(1,3,'2021-06-01 12:58:33'),(1,3,'2021-06-01 16:06:51'),(1,3,'2021-06-02 10:01:31'),(1,3,'2021-06-09 16:22:19'),(1,3,'2021-06-10 12:57:38'),(1,3,'2021-06-11 18:09:16'),(1,3,'2021-06-12 15:29:06'),(1,3,'2021-06-12 16:08:29'),(1,3,'2021-06-13 10:14:07'),(1,3,'2021-06-13 16:44:14'),(1,3,'2021-06-13 21:17:21'),(1,3,'2021-06-13 21:41:56'),(1,3,'2021-06-14 12:06:05'),(1,3,'2021-06-15 12:09:37'),(1,3,'2021-06-16 15:50:53'),(1,3,'2021-06-17 11:08:44'),(1,3,'2021-06-17 12:13:39'),(3,3,'2021-05-09 11:53:53'),(3,3,'2021-05-09 12:10:14'),(3,3,'2021-05-10 17:05:38'),(3,3,'2021-05-10 19:10:05'),(3,3,'2021-05-21 09:57:32'),(3,3,'2021-06-13 20:55:55'),(3,3,'2021-06-13 21:17:37'),(3,3,'2021-06-14 16:55:01'),(3,3,'2021-06-17 12:09:31');
/*!40000 ALTER TABLE `user_actions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `iduser` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(255) NOT NULL,
  `email` varchar(90) NOT NULL,
  `perfil` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  PRIMARY KEY (`iduser`),
  UNIQUE KEY `emailRegistro_UNIQUE` (`nombre`),
  UNIQUE KEY `nombreRegistro_UNIQUE` (`iduser`),
  UNIQUE KEY `email_UNIQUE` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES (1,'admin','admin@gmail.com','Administrador','$2b$12$C5g9XKZI258N.xEM6xbxN.e5fB0n62omhxbG6f6vtoVOZ6ysO6Ee.'),(3,'operador','operador@gmail.com','Operador','$2b$12$C5g9XKZI258N.xEM6xbxN.hjsb6.US5R5lSwHgiugNSucOI10vLo2'),(27,'analista2','analista@gmail.com','Analista','$2b$12$OcJ9kAPAJLroUQLeyqdWPeeY2cy7zRM9bxv8.BsEHeK9sDH/P56qy'),(30,'ana','anavelatroyaa@gmail.com','Analista','$2b$12$pqLUEJiLWM7G0.wLaAr06.qtV7R5DgN9QxcUEL1ZX07wA.ijuOT/y');
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2021-06-17 12:36:39
