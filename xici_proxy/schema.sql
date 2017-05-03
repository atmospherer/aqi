PRAGMA foreign_keys = OFF;

-- ----------------------------
-- Table structure for aqi
-- ----------------------------
DROP TABLE IF EXISTS "main"."aqi";
CREATE TABLE aqi (
            ID INTEGER NOT NULL PRIMARY KEY,
            division UNSIGNED BIG INT(10) NOT NULL,
            areaName VARCHAR(12) DEFAULT NULL,
            value INTEGER NOT NULL,
            pollutant INTEGER DEFAULT NULL,
            recordDate DATE NOT NULL,
            _fetchDate DATE NOT NULL,
            source VARCHAR(8) DEFAULT NULL
        );

-- ----------------------------
-- Indexes structure for table aqi
-- ----------------------------
CREATE INDEX "main"."aqiAreaNameIdx"
ON "aqi" ("areaName" ASC);
CREATE INDEX "main"."aqiDivisionIdx"
ON "aqi" ("division" ASC);
CREATE INDEX "main"."aqiRecordTimeIdx"
ON "aqi" ("recordDate" ASC);

-- ----------------------------
-- Table structure for aqi_data
-- ----------------------------
DROP TABLE IF EXISTS "main"."aqi_data";
CREATE TABLE "aqi_data" (
"id"  INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
"area"  TEXT NOT NULL,
"value"  INTEGER NOT NULL,
"pollutant"  TEXT,
"record_date"  INTEGER,
"fetch_date"  INTEGER
);

-- ----------------------------
-- Indexes structure for table aqi_data
-- ----------------------------
CREATE INDEX "main"."idx_aqi_data_record_date"
ON "aqi_data" ("record_date" ASC);
CREATE UNIQUE INDEX "main"."uk_aqi_data_area_record_date"
ON "aqi_data" ("area" ASC, "record_date" ASC);

-- ----------------------------
-- Table structure for areas
-- ----------------------------
DROP TABLE IF EXISTS "main"."areas";
CREATE TABLE areas (
            ID INTEGER NOT NULL PRIMARY KEY,
            division UNSIGNED BIG INT(10) NOT NULL,
            name VARCHAR(12) NOT NULL,
            engName VARCHAR(64),
            pinyinName VARCHAR(64),
            bottom BOOLEAN DEFAULT FALSE,
            superior UNSIGNED BIG INT(10)
        );

-- ----------------------------
-- Indexes structure for table areas
-- ----------------------------
CREATE INDEX "main"."areaDivisionIdx"
ON "areas" ("division" ASC);
CREATE INDEX "main"."areaNameIdx"
ON "areas" ("name" ASC);

-- ----------------------------
-- Table structure for pollutant
-- ----------------------------
DROP TABLE IF EXISTS "main"."pollutant";
CREATE TABLE pollutant (
            ID INTEGER NOT NULL PRIMARY KEY,
            name VARCHAR(32) NOT NULL
        );

-- ----------------------------
-- Indexes structure for table pollutant
-- ----------------------------
CREATE INDEX "main"."aqiPollutantNameIdx"
ON "pollutant" ("name" ASC);
