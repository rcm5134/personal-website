CREATE TABLE IF NOT EXISTS `skills` (
`skill_id`         int(11)     NOT NULL auto_increment	  COMMENT 'the id of skill',
`proj_id`          int(11)     NOT NULL                   COMMENT 'the id of project this skill belongs to',
`name`             varchar(20) NOT NULL                   COMMENT 'the name of the skill',
PRIMARY KEY (`skill_id`),
FOREIGN KEY (`proj_id`) REFERENCES projects(`proj_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COMMENT="Contains skills used in projects";