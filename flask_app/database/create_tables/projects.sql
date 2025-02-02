CREATE TABLE IF NOT EXISTS `projects` (
`proj_id`          int(11)     NOT NULL auto_increment	  COMMENT 'the id of project',
`name`             varchar(20) NOT NULL                   COMMENT 'the name of the project',
`image`            varchar(20) NOT NULL                   COMMENT 'the image of the project',
`description`      varchar(20) NOT NULL                   COMMENT 'the description of the project',
`link`             varchar(30) NOT NULL                   COMMENT 'the link to the project',

PRIMARY KEY (`proj_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COMMENT="Contains project information";