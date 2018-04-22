import psycopg2

def run_queries(landname):
    country = landname.lower()

    #connect to postgres
    conn = psycopg2.connect(database="raster_database", user="postgres", host="localhost", password="postgres")
    cur = conn.cursor()

    #----- Queries ---------------------------------------------------------------------------------------------------

    # Null value not 0:
    #print("Dropping pop raster nodata constraint ")
    #cur.execute("ALTER TABLE {0}_2015 DROP CONSTRAINT IF EXISTS Enforce_nodata_values_rast;".format(country))
    #conn.commit()

    #print("Setting raster nodata to NULL")
    #cur.execute("UPDATE {0}_2015 SET rast = ST_SetBandNoDataValue(rast,1, NULL);".format(country))
    #conn.commit()

    # Vector grid from raster:
    #print("Creating vector grid from raster")
    #cur.execute("SELECT (gv).x, (gv).y, (gv).val, (gv).geom \
                #into {0}_2015vector \
                #FROM (SELECT ST_PixelAsPolygons(rast, 1, TRUE \
                #) gv from {0}_2015 \
                #) output;".format(country))
    #conn.commit()

    #Creating index on vector grid
    print("Creating index on vector grid")
    cur.execute("CREATE INDEX {0}_2015vector_gix ON {0}_2015vector USING GIST (geom);".format(country))
    conn.commit()

    print("Creating bbox from administrative areas")
    # bbox from administrative(+buffer):
    cur.execute("create table {0}_bbox as \
                SELECT ST_Buffer(ST_SetSRID(ST_Extent(geom),54009) \
                ,250,'endcap=square join=mitre') as geom FROM {0}_adm;".format(country))
    conn.commit()

    print("Creating index on bounding box")
    cur.execute("CREATE INDEX {0}_bbox_gix ON {0}_bbox USING GIST(geom);".format(country))
    conn.commit()

    print("Creating ocean around country")
    # Ocean from administrative + bbox:
    cur.execute("Select ST_Subdivide(ST_Difference({0}_bbox.geom, {0}_adm.geom)) as geom \
                into subdivided_{0}_ocean FROM {0}_bbox, {0}_adm;".format(country))
    conn.commit()

    print("Creating waterbodies")
    # Waterbodies:
    cur.execute("create table {0}_water as \
                with a as ( \
                select eu_lakes_{0}.name, ST_Intersection(eu_lakes_{0}.geom, {0}_adm.geom) as geom \
                FROM eu_lakes_{0}, {0}_adm \
                where ST_Intersects(eu_lakes_{0}.geom, {0}_adm.geom)) \
                select geom FROM subdivided_{0}_ocean \
                UNION \
                select ST_Subdivide(ST_Union(geom)) from a;".format(country))
    conn.commit()

    print("Creating index on water layer")
    cur.execute("CREATE INDEX {0}_water_gix ON {0}_water USING GIST (geom);".format(country))
    conn.commit()

    print("Creating water cover table")
    # Watercover percentage:
    cur.execute("Create table {0}_water_cover as \
                SELECT * \
                FROM {0}_2015vector;".format(country))
    conn.commit()

    print("Set water cover layer default pixel value to 0")
    cur.execute("Alter table {0}_water_cover ADD column water_cover double precision default 0, add column id SERIAL PRIMARY KEY;".format(country))
    conn.commit()

    print("Calculating water cover percentage")
    cur.execute("With i as (SELECT {0}_water_cover.id, sum(ST_AREA(ST_INTERSECTION({0}_water_cover.geom, {0}_water.geom))/62500*100) as water \
                FROM {0}_water_cover, {0}_water WHERE ST_intersects({0}_water_cover.geom, {0}_water.geom) \
                GROUP BY id) \
                UPDATE {0}_water_cover SET water_cover = water from i WHERE i.id = {0}_water_cover.id;".format(country))
    conn.commit()

    print("Adding road distance column")
    # Distance to Roads into water cover vector:
    # cur.execute("Alter table {0}_water_cover drop column rdist;".format(country)) #does not exist
    cur.execute("Alter table {0}_water_cover ADD column rdist double precision default 99999999;".format(country))
    conn.commit()

    print("Calculating road distance")
    cur.execute("With a as (SELECT ST_Transform(ST_SetSRID(groads.geom, 4326), 54009) as geom from groads), \
                b as (Select a.geom as geom from a, {0}_adm where ST_DWithin({0}_adm.geom, a.geom, 1)), \
                c as (Select id, ST_Centroid({0}_water_cover.geom) as geom \
                from {0}_water_cover, {0}_adm where {0}_water_cover.water_cover < 99.999), \
                d as (SELECT Distinct ON (c.id) c.id as id, \
                ST_Distance(c.geom, b.geom) AS r_dist from b, c \
                WHERE st_DWithin(c.geom, b.geom, 30000) order by c.id, r_dist asc) \
                UPDATE {0}_water_cover SET rdist = r_dist from d WHERE d.id = {0}_water_cover.id;".format(country))
    conn.commit()

    # Corine 2012:
    print("Adding corine cover 2012 column")
    cur.execute("Alter table {0}_water_cover ADD column corine_cover double precision default 0;".format(country))
    conn.commit()

    print("Preparing corine cover layer 2012")
    cur.execute("With a as ( \
                SELECT objectid, code_12, area_ha, st_transform(geom, 54009) as geom from corine), \
                b as (Select a.* from a, {0}_adm WHERE ST_Intersects(a.geom, {0}_adm.geom)), \
                i as (SELECT {0}_water_cover.id, sum(ST_AREA(ST_INTERSECTION({0}_water_cover.geom, b.geom))/62500*100) as corinecover \
                FROM {0}_water_cover, b WHERE ST_intersects({0}_water_cover.geom, b.geom) \
                GROUP BY id) \
                UPDATE {0}_water_cover SET corine_cover = corinecover from i WHERE i.id = {0}_water_cover.id;".format(country))
    conn.commit()

    # Corine 1990:
    print("Adding corine cover 1990 column")
    cur.execute("Alter table {0}_water_cover ADD column corine_cover90 double precision default 0;".format(country))
    conn.commit()

    print("Preparing corine layer 1990")
    cur.execute("With a as ( \
                SELECT objectid, code_90, area_ha, st_transform(geom, 54009) as geom from corine90), \
                b as (Select a.* from a, {0}_adm WHERE ST_Intersects(a.geom, {0}_adm.geom)), \
                i as (SELECT {0}_water_cover.id, sum(ST_AREA(ST_INTERSECTION({0}_water_cover.geom, b.geom))/62500*100) as corinecover \
                FROM {0}_water_cover, b WHERE ST_intersects({0}_water_cover.geom, b.geom) \
                GROUP BY id) \
                UPDATE {0}_water_cover SET corine_cover90 = corinecover from i WHERE i.id = {0}_water_cover.id;".format(country))
    conn.commit()

    #closing connection
    cur.close()
    conn.close()

