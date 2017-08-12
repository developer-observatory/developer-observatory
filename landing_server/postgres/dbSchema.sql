\connect "notebook";

CREATE USER created_instances_user WITH PASSWORD '%pwUser1%';
CREATE USER insert_user WITH PASSWORD '%pwUser2%';
CREATE USER read_only_user WITH PASSWORD '%pwUser3%';

CREATE TABLE IF NOT EXISTS "createdInstances" (
    id serial primary key,
    userid text,
    ip text NOT NULL,
    time timestamp without time zone,
    ec2instance text,
    category integer,
    condition integer,
    instanceid text,
    terminated boolean DEFAULT false,
    heartbeat timestamp without time zone default now(),
    "instanceTerminated" boolean DEFAULT false
);

DROP TABLE IF EXISTS "conditions";
CREATE TABLE "conditions" (category integer, condition integer, filename text, hash text, PRIMARY KEY(category, condition));

CREATE TABLE IF NOT EXISTS "copy_pasted_code" (
    id serial primary key,
    userid character varying,
    token character varying,
    tasknum character varying,
    cellid character varying,
    code character varying,
    "time" timestamp without time zone
);
    
CREATE TABLE IF NOT EXISTS "jupyter" (
    id serial primary key,
    userid character varying,
    token character varying,
    code json,
    "time" json,
    status character varying(1),
    date timestamp without time zone
);


REVOKE ALL ON ALL TABLES IN SCHEMA public FROM PUBLIC;
ALTER TABLE "createdInstances" OWNER TO created_instances_user;
ALTER TABLE "jupyter" OWNER TO insert_user;
ALTER TABLE "copy_pasted_code" OWNER TO insert_user;
GRANT SELECT ON "conditions" TO created_instances_user;
GRANT SELECT ON "conditions" TO insert_user;
GRANT SELECT ON "conditions" TO read_only_user;
GRANT SELECT,UPDATE,INSERT ON "createdInstances" TO created_instances_user;
GRANT SELECT,UPDATE ON "createdInstances" TO insert_user;
GRANT SELECT ON "createdInstances" TO read_only_user;
GRANT INSERT ON "jupyter" TO insert_user;
GRANT SELECT ON "jupyter" TO read_only_user;
GRANT INSERT ON "copy_pasted_code" TO insert_user;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public to insert_user;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public to read_only_user;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public to created_instances_user;
