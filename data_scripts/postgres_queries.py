import psycopg2
import time
def run_queries(landname):
    country = landname.lower()

    #connect to postgres
    conn = psycopg2.connect(database="raster_database", user="postgres", host="localhost", password="postgres")
    cur = conn.cursor()

    # Queries ----------------------------------------------------------------------------------------------------------

    # Creating necessary tables ----------------------------------------------------------------------------------------
    print("---------- Creating necessary tables ----------")
    print("Creating {0} bounding box layer from administrative areas".format(country))
    # bbox from administrative(+buffer):
    cur.execute("create table {0}_bbox as \
                    SELECT ST_Buffer(ST_SetSRID(ST_Extent(geom),54009) \
                    ,250,'endcap=square join=mitre') as geom FROM {0}_adm;".format(country))  # 45 msec
    conn.commit()

    print("Creating {0} ocean layer".format(country))
    # Ocean from administrative + bbox:
    cur.execute("Select ST_Subdivide(ST_Difference({0}_bbox.geom, {0}_adm.geom)) as geom \
                    into subdivided_{0}_ocean FROM {0}_bbox, {0}_adm;".format(country))  # 6.6 sec
    conn.commit()

    print("Creating {0} cover analysis table".format(country))
    # Watercover percentage:
    cur.execute("Create table {0}_cover_analysis as \
                    SELECT * \
                    FROM {0}_2015vector;".format(country))  # 4.3 sec
    conn.commit()

    print("Creating {0} waterbodies layer".format(country))
    # Creating waterbodies layer
    cur.execute("create table {0}_water as \
                    with a as ( \
                    select eu_lakes_{0}.name, ST_Intersection(eu_lakes_{0}.geom, {0}_adm.geom) as geom \
                    FROM eu_lakes_{0}, {0}_adm \
                    where ST_Intersects(eu_lakes_{0}.geom, {0}_adm.geom)) \
                    select geom FROM subdivided_{0}_ocean \
                    UNION \
                    select ST_Subdivide(ST_Union(geom)) from a;".format(country))  # 3.32 min
    conn.commit()

    # Indexing necessary tables ----------------------------------------------------------------------------------------
    print("---------- Indexing necessary tables ----------")
    #Creating index on vector grid
    print("Creating gist index on {0} vector grid".format(country))
    cur.execute("CREATE INDEX {0}_2015vector_gix ON {0}_2015vector USING GIST (geom);".format(country)) # 54 sec
    conn.commit()

    print("Creating gist index on {0} bounding box layer".format(country))
    # Creating index on administrative areas bounding box layer
    cur.execute("CREATE INDEX {0}_bbox_gix ON {0}_bbox USING GIST(geom);".format(country)) # 22 msec
    conn.commit()

    print("Creating gist index on {0} water layer".format(country))
    #Creating index on water layer
    cur.execute("CREATE INDEX {0}_water_gix ON {0}_water USING GIST (geom);".format(country)) # 32 msec
    conn.commit()

    print("Creating id index on {0}_cover_analysis layer")
    # Create index on country water cover id
    cur.execute("CREATE INDEX {0}_cover_analysis_id_index ON {0}_cover_analysis (id);".format(country))  # 4.8 sec
    conn.commit()

    # print("Creating gist index on {0}_cover_analysis layer".format(country))
    # # Creating index on water layer
    # cur.execute("CREATE INDEX {0}_cover_analysis_gix ON {0}_cover_analysis USING GIST (geom);".format(country))
    # conn.commit()

    # -------------------- Adding necessary columns to country cover analysis table --------------------
    print("---------- Adding necessary columns to {0}_cover_analysis table ----------".format(country))
    print("Adding water cover column")
    # Adding water cover column to cover analysis table
    cur.execute("Alter table {0}_cover_analysis ADD column water_cover double precision default 0, add column id SERIAL PRIMARY KEY;".format(country)) # 11.3 sec
    conn.commit()

    print("Adding road distance column")
    # Adding road distance column to cover analysis table
    cur.execute(
        "Alter table {0}_cover_analysis ADD column rdist double precision default 99999999;".format(country))  # 14.8 sec
    conn.commit()

    print("Adding water cover 1990 column")
    # Adding water cover 1990 to country cover analysis table
    cur.execute("Alter table {0}_cover_analysis ADD column corine_cover90 double precision default 0;".format(country))
    conn.commit()

    print("Adding corine cover 2012 column")
    # Adding water cover 2012 to country cover analysis table
    cur.execute("Alter table {0}_cover_analysis ADD column corine_cover double precision default 0;".format(country))
    conn.commit()

    # getting id number of chunks within the iteration grid covering the country
    ids = []
    cur.execute("SELECT gid FROM {0}_iteration_grid;".format(country))
    chunk_id = cur.fetchall()

    # saving ids to list
    for id in chunk_id:
        ids.append(id[0])

    print("-------------------- PROCESSING COVERAGE ANALYSIS: {0} consists of {1} big chunks --------------------".format(country, len(ids)))

    # Calculating water cover percentage -------------------------------------------------------------------------------

    print("---------- Calculating water cover percentage ----------")
    # start total query time timer
    start_query_time = time.time()

    # preparing water table by subdividing country water table
    print("Creating subdivided water table")
    cur.execute(
        "CREATE TABLE subdivided_{0}_water AS (SELECT ST_Subdivide({0}_water.geom, 40) AS geom FROM {0}_water)".format(
            country))

    # create index on water
    cur.execute("CREATE INDEX subdivided_{0}_water_gix ON subdivided_{0}_water USING GIST (geom);".format(country))

    # iterating through chunks
    for chunk in ids:
        # check if chunk is pure ocean
        cur.execute("SELECT {0}_iteration_grid.gid \
                            FROM {0}_iteration_grid, {0}_adm \
                            WHERE ST_Intersects({0}_iteration_grid.geom, {0}_adm.geom) \
                            AND {0}_iteration_grid.gid = {1};".format(country, chunk))
        result_check = cur.rowcount

        if result_check == 0:
            print("Chunk number: {0} \ {1} is empty, setting water = 100 procent".format(chunk, len(ids)))
            # Setting the values of the whole chunk in country_cover_analysis - water_cover to 100 procent
            cur.execute("WITH a AS (SELECT {0}_cover_analysis.id, {0}_cover_analysis.geom \
                        FROM {0}_cover_analysis, {0}_iteration_grid \
                        WHERE {0}_iteration_grid.gid = {1} \
                        AND ST_Intersects({0}_cover_analysis.geom, {0}_iteration_grid.geom)) \
                        UPDATE {0}_cover_analysis SET water_cover = 100 FROM a WHERE a.id = {0}_cover_analysis.id;".format(
                country, chunk))
        else:
            print("Chunk number: {0} \ {1} is not empty, Processing...".format(chunk, len(ids)))
            # start single chunk query time timer
            t0 = time.time()
            # select cells that is within each chunk and create a new table
            cur.execute("CREATE TABLE chunk_nr{1} AS (SELECT {0}_cover_analysis.id, {0}_cover_analysis.geom \
                            FROM {0}_cover_analysis, {0}_iteration_grid \
                            WHERE {0}_iteration_grid.gid = {1} \
                            AND ST_Intersects({0}_cover_analysis.geom, {0}_iteration_grid.geom));".format(country,
                                                                                                          chunk))  # 1.6 sec
            conn.commit()

            # create index on chunk
            cur.execute("CREATE INDEX chunk_nr{0}_gix ON chunk_nr{0} USING GIST (geom);".format(chunk))  # 464 msec
            conn.commit()

            # calculating water cover percentage
            cur.execute("WITH a AS (SELECT chunk_nr{1}.id, sum(ST_AREA(ST_INTERSECTION(chunk_nr{1}.geom, subdivided_{0}_water.geom))/62500*100) as water \
                            FROM chunk_nr{1}, subdivided_{0}_water WHERE ST_intersects(chunk_nr{1}.geom, subdivided_{0}_water.geom) \
                            GROUP BY id) \
                            UPDATE {0}_cover_analysis SET water_cover = water from a \
                            WHERE a.id = {0}_cover_analysis.id;".format(country, chunk))

            # drop chunk_nr table
            cur.execute("DROP TABLE chunk_nr{0};".format(chunk))  # 22 ms
            conn.commit()

            # stop single chunk query time timer
            t1 = time.time()

            # calculate single chunk query time in minutes
            total = (t1 - t0) / 60
            print("Chunk number: {0} took {1} minutes to process".format(chunk, total))

    # stop total query time timer
    stop_query_time = time.time()

    # calculate total query time in minutes
    total_query_time = (stop_query_time - start_query_time) / 60
    print("Total water cover query time : {0} minutes".format(total_query_time))

    # drop subdivided water table
    cur.execute("DROP TABLE subdivided_{0}_water;".format(country))  # 22 ms
    conn.commit()

    # Calculating road distance ----------------------------------------------------------------------------------------
    print("---------- Calculating road distance ----------")
    # start total query time timer
    start_query_time = time.time()
    print("Creating table with roads within the country")
    #Creating table with roads within the country
    cur.execute("CREATE TABLE {0}_iterate_roads AS (SELECT groads.gid, ST_Transform(ST_SetSRID(groads.geom, 4326), 54009) AS geom FROM groads, {0}_adm \
                WHERE ST_DWithin({0}_adm.geom, ST_Transform(ST_SetSRID(groads.geom, 4326), 54009), 1));".format(country))  # 1.10 min

    # creating index on roads table
    cur.execute("CREATE INDEX {0}_iterate_roads_gix ON {0}_iterate_roads USING GIST (geom);".format(country))  # 21 ms
    conn.commit()


    # iterating through chunks
    for chunk in ids:
        # start single chunk query time timer
        t0 = time.time()

        # Create table containing centroids of the original small grid within the land cover of the country
        cur.execute("CREATE TABLE chunk_nr{1} AS (SELECT id, ST_Centroid({0}_cover_analysis.geom) AS geom \
                    FROM {0}_cover_analysis, {0}_iteration_grid \
                    WHERE {0}_iteration_grid.gid = {1} \
                    AND ST_Intersects({0}_iteration_grid.geom, {0}_cover_analysis.geom) \
                    AND {0}_cover_analysis.water_cover < 99.999);".format(country, chunk))  # 1.7 sec
        # check if chunk query above returns values or is empty
        result_check = cur.rowcount

        if result_check == 0:
            print("Chunk number: {0} \ {1} is empty, moving to next chunk".format(chunk, len(ids)))
            conn.rollback()
        else:
            conn.commit()
            print("Chunk number: {0} \ {1} is not empty, Processing...".format(chunk, len(ids)))

            # Index chunk
            cur.execute("CREATE INDEX chunk_nr{0}_gix ON chunk_nr{0} USING GIST (geom);".format(chunk))  # 175 ms
            conn.commit()

            # Create table containing water_cover cell id and distance ALL
            cur.execute("WITH a AS (SELECT Distinct ON (chunk_nr{1}.id) chunk_nr{1}.id as id, \
            ST_Distance(chunk_nr{1}.geom, {0}_iterate_roads.geom) AS r_dist from {0}_iterate_roads, chunk_nr{1}, {0}_adm \
            WHERE ST_Intersects(chunk_nr{1}.geom, {0}_adm.geom) AND st_DWithin(chunk_nr{1}.geom, {0}_iterate_roads.geom, 30000) order by chunk_nr{1}.id, r_dist asc) \
            UPDATE {0}_cover_analysis SET rdist = r_dist from a WHERE a.id = {0}_cover_analysis.id;".format(country, chunk))  # 4.1 sec
            conn.commit()

            # Drop chunk_nr table
            cur.execute("DROP TABLE chunk_nr{0};".format(chunk))  # 22 ms
            conn.commit()

            # stop single chunk query time timer
            t1 = time.time()

            # calculate single chunk query time in minutes
            total = (t1 - t0) / 60
            print("Chunk number: {0} took {1} minutes to process".format(chunk, total))

    # stop total query time timer
    stop_query_time = time.time()

    #calculate total query time in minutes
    total_query_time = (stop_query_time - start_query_time) / 60
    print("Total road distance query time : {0} minutes".format(total_query_time))

    # Drop roads iteration table
    cur.execute("DROP TABLE {0}_iterate_roads;".format(country))
    conn.commit()

    # Calculating corine 1990 coverage ---------------------------------------------------------------------------------
    print("---------- Calculating corine 1990 coverage ----------")
    # start total query time timer
    start_query_time = time.time()

    # Transforming corine 1990 to srs 54009, subdividing geom and selecting everything that intersects with the country
    print("Creating subdivided corine 1990 layer")
    cur.execute("CREATE TABLE subdivided_{0}_corine90 AS (SELECT corine90.objectid, code_90, area_ha, \
                    ST_Subdivide(ST_Transform(corine90.geom, 54009), 30) AS geom FROM corine90, {0}_adm \
                    WHERE ST_Intersects(ST_Transform(corine90.geom, 54009), {0}_adm.geom));".format(country))
    conn.commit()

    # Index subdivided corine table
    print("Creating index on subdivided corine 1990 layer")
    cur.execute("CREATE INDEX subdivided_{0}_corine90_gix ON subdivided_{0}_corine90 USING GIST (geom);".format(country))  # 175 ms
    conn.commit()

    # iterate through chunks
    for chunk in ids:
        # start single chunk query time timer
        t0 = time.time()

        # Check if chunk intersects with corine cover layer
        cur.execute("SELECT {0}_iteration_grid.gid \
                         FROM {0}_iteration_grid, subdivided_{0}_corine90 \
                         WHERE ST_Intersects({0}_iteration_grid.geom, subdivided_{0}_corine90.geom) \
                         AND {0}_iteration_grid.gid = {1};".format(country, chunk))
        result_check = cur.rowcount

        if result_check == 0:
            print("Chunk number: {0} \ {1} is empty, moving to next chunk".format(chunk, len(ids)))

        else:
            print("Chunk number: {0} \ {1} is not empty, Processing...".format(chunk, len(ids)))

            # select cells that is within each chunk and create a new table
            cur.execute("CREATE TABLE chunk_nr{1} AS (SELECT {0}_cover_analysis.id, {0}_cover_analysis.geom \
                             FROM {0}_cover_analysis, {0}_iteration_grid \
                             WHERE {0}_iteration_grid.gid = {1} \
                             AND ST_Intersects({0}_cover_analysis.geom, {0}_iteration_grid.geom));".format(country, chunk))  # 1.6 sec
            conn.commit()

            # Index chunk
            cur.execute("CREATE INDEX chunk_nr{0}_gix ON chunk_nr{0} USING GIST (geom);".format(chunk))  # 175 ms
            conn.commit()

            # calculating corine 1990 coverage
            cur.execute("WITH a AS (SELECT chunk_nr{1}.id, sum(ST_AREA(ST_INTERSECTION(chunk_nr{1}.geom, subdivided_{0}_corine90.geom))/62500*100) as corinecover \
                            FROM chunk_nr{1}, subdivided_{0}_corine90 WHERE ST_intersects(chunk_nr{1}.geom, subdivided_{0}_corine90.geom) \
                            GROUP BY id) \
                            UPDATE {0}_cover_analysis SET corine_cover = corinecover from a WHERE a.id = {0}_cover_analysis.id;".format(country, chunk))
            conn.commit()

            # stop single chunk time timer
            t1 = time.time()

            # calculate single chunk query time in minutes
            total = (t1 - t0) / 60
            print("Chunk number: {0} took {1} minutes to process".format(chunk, total))

            # Drop chunk_nr table
            cur.execute("DROP TABLE chunk_nr{0};".format(chunk))  # 22 ms
            conn.commit()

    # stop total query time timer
    stop_query_time = time.time()

    #calculate total query time in minutes
    total_query_time = (stop_query_time - start_query_time) / 60
    print("Total corine cover 1990 query time : {0} minutes".format(total_query_time))

    # Drop subdivided country corine table
    cur.execute("DROP TABLE subdivided_{0}_corine90;".format(country))  # 22 ms
    conn.commit()

    # Calculating corine 2012 coverage ---------------------------------------------------------------------------------
    print("---------- Calculating corine 2012 coverage ----------")
    # start total query time timer
    start_query_time = time.time()

    print("Creating subdivided corine 2012 layer")
    cur.execute("CREATE TABLE subdivided_{0}_corine AS (SELECT corine.objectid, code_12, area_ha, \
                    ST_Subdivide(ST_Transform(corine.geom, 54009), 30) AS geom FROM corine, {0}_adm \
                    WHERE ST_Intersects(ST_Transform(corine.geom, 54009), {0}_adm.geom));".format(country))
    conn.commit()

    # Index subdivided corine 2012 table
    print("Creating index on subdivided corine 2012 layer")
    cur.execute("CREATE INDEX subdivided_{0}_corine_gix ON subdivided_{0}_corine USING GIST (geom);".format(country))  # 175 ms
    conn.commit()

    # iterate through chunks
    for chunk in ids:
        # Check if chunk intersects with corine cover layer
        cur.execute("SELECT {0}_iteration_grid.gid \
                         FROM {0}_iteration_grid, subdivided_{0}_corine \
                         WHERE ST_Intersects({0}_iteration_grid.geom, subdivided_{0}_corine.geom) \
                         AND {0}_iteration_grid.gid = {1};".format(country, chunk))
        result_check = cur.rowcount

        if result_check == 0:
            print("Chunk number: {0} \ {1} is empty, moving to next chunk".format(chunk, len(ids)))

        else:
            print("Chunk number: {0} \ {1} is not empty, Processing...".format(chunk, len(ids)))
            # start single chunk query time timer
            t0 = time.time()

            # select cells that is within each chunk and create a new table
            cur.execute("CREATE TABLE chunk_nr{1} AS (SELECT {0}_cover_analysis.id, {0}_cover_analysis.geom \
                             FROM {0}_cover_analysis, {0}_iteration_grid \
                             WHERE {0}_iteration_grid.gid = {1} \
                             AND ST_Intersects({0}_cover_analysis.geom, {0}_iteration_grid.geom));".format(country, chunk))  # 1.6 sec
            conn.commit()

            # Index chunk
            cur.execute("CREATE INDEX chunk_nr{0}_gix ON chunk_nr{0} USING GIST (geom);".format(chunk))  # 175 ms
            conn.commit()

            # calculating corine 2012 coverage
            cur.execute("WITH a AS (SELECT chunk_nr{1}.id, sum(ST_AREA(ST_INTERSECTION(chunk_nr{1}.geom, subdivided_{0}_corine.geom))/62500*100) as corinecover \
                            FROM chunk_nr{1}, subdivided_{0}_corine WHERE ST_intersects(chunk_nr{1}.geom, subdivided_{0}_corine.geom) \
                            GROUP BY id) \
                            UPDATE {0}_cover_analysis SET corine_cover = corinecover from a WHERE a.id = {0}_cover_analysis.id;".format(country, chunk))
            conn.commit()

            # stop single chunk query time timer
            t1 = time.time()
            # calculate single chunk query time in minutes
            total = (t1 - t0) / 60
            print("Chunk number: {0} took {1} minutes to process".format(chunk, total))

            # Drop chunk_nr table
            cur.execute("DROP TABLE chunk_nr{0};".format(chunk))  # 22 ms
            conn.commit()

    # stop total query time timer
    stop_query_time = time.time()

    # calculate total query time in minutes
    total_query_time = (stop_query_time - start_query_time) / 60
    print("Total road distance query time : {0} minutes".format(total_query_time))

    # Drop subdivided country corine table
    cur.execute("DROP TABLE subdivided_{0}_corine;".format(country))  # 22 ms
    conn.commit()

    # closing connection
    cur.close()
    conn.close()