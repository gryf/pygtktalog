--
-- PostgreSQL database dump
--

-- Started on 2006-08-09 10:58:37 CEST

SET client_encoding = 'LATIN2';
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- TOC entry 1567 (class 0 OID 0)
-- Dependencies: 5
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA public IS 'Standard public schema';


--
-- TOC entry 276 (class 2612 OID 100455)
-- Name: plpgsql; Type: PROCEDURAL LANGUAGE; Schema: -; Owner: 
--

CREATE PROCEDURAL LANGUAGE plpgsql;


SET search_path = public, pg_catalog;

--
-- TOC entry 11 (class 1255 OID 100457)
-- Dependencies: 5 276
-- Name: lang_asarray(character varying, character varying); Type: FUNCTION; Schema: public; Owner: pgsql
--

CREATE FUNCTION lang_asarray(character varying, character varying) RETURNS text
    AS $_$
DECLARE
    id_pliku ALIAS FOR $1;
    table_name ALIAS FOR $2;
    query text;
    rec record;
    str varchar;
    arr text;
BEGIN
        query := 'select short from '||table_name||' a left join lang b using(id_lang) where id_pliku = '||id_pliku||' order by short';
    str:='';
    FOR rec IN EXECUTE query LOOP
        str := str ||rec.short||', ';
    END LOOP;
        SELECT trim(trailing ', ' from str) INTO str;
    SELECT INTO arr str;
    RETURN arr;
END;
$_$
    LANGUAGE plpgsql;


--
-- TOC entry 12 (class 1255 OID 100458)
-- Dependencies: 5
-- Name: plpgsql_call_handler(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION plpgsql_call_handler() RETURNS language_handler
    AS '$libdir/plpgsql', 'plpgsql_call_handler'
    LANGUAGE c;


--
-- TOC entry 13 (class 1255 OID 100459)
-- Dependencies: 5
-- Name: plpgsql_validator(oid); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION plpgsql_validator(oid) RETURNS void
    AS '$libdir/plpgsql', 'plpgsql_validator'
    LANGUAGE c;


SET default_tablespace = '';

SET default_with_oids = true;

--
-- TOC entry 1210 (class 1259 OID 100462)
-- Dependencies: 5
-- Name: dub; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE dub (
    id_pliku integer,
    id_lang integer
);


--
-- TOC entry 1212 (class 1259 OID 100466)
-- Dependencies: 5
-- Name: genre; Type: TABLE; Schema: public; Owner: pgsql; Tablespace: 
--

CREATE TABLE genre (
    id_genre serial NOT NULL,
    nazwa text,
    opis text
);


--
-- TOC entry 1213 (class 1259 OID 100472)
-- Dependencies: 5
-- Name: genre_tytul; Type: TABLE; Schema: public; Owner: pgsql; Tablespace: 
--

CREATE TABLE genre_tytul (
    id_tytulu integer,
    id_genre integer
);


SET default_with_oids = false;

--
-- TOC entry 1215 (class 1259 OID 100476)
-- Dependencies: 5
-- Name: grupa; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE grupa (
    id_grupy serial NOT NULL,
    nazwa_grupy text,
    short text
);


--
-- TOC entry 1216 (class 1259 OID 100482)
-- Dependencies: 5
-- Name: grupa_plik; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE grupa_plik (
    id_pliku integer,
    id_grupy integer
);


SET default_with_oids = true;

--
-- TOC entry 1218 (class 1259 OID 100486)
-- Dependencies: 5
-- Name: lang; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE lang (
    id_lang serial NOT NULL,
    nazwa text,
    short text
);


--
-- TOC entry 1219 (class 1259 OID 100492)
-- Dependencies: 1552 5
-- Name: nazwa_tytulu; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE nazwa_tytulu (
    id_tytulu integer,
    tytul text,
    alt boolean DEFAULT false
);


--
-- TOC entry 1221 (class 1259 OID 100500)
-- Dependencies: 1554 1555 5
-- Name: plik; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE plik (
    id_pliku serial NOT NULL,
    nazwa_pliku text,
    rozdz text,
    vcodec text,
    acodec text,
    rozmiar integer,
    jakosc integer,
    uwagi text,
    id_tytulu integer,
    aktywny boolean DEFAULT true,
    data_dodania timestamp without time zone DEFAULT now()
);


--
-- TOC entry 1222 (class 1259 OID 100508)
-- Dependencies: 5
-- Name: plyta; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE plyta (
    nr_pudelka integer,
    id_pliku integer,
    nr_plyty text
);


--
-- TOC entry 1224 (class 1259 OID 100520)
-- Dependencies: 5
-- Name: rodzaj; Type: TABLE; Schema: public; Owner: pgsql; Tablespace: 
--

CREATE TABLE rodzaj (
    id_rodzaju serial NOT NULL,
    nazwa_rodzaju text
);


--
-- TOC entry 1225 (class 1259 OID 100526)
-- Dependencies: 5
-- Name: sub; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE sub (
    id_pliku integer,
    id_lang integer
);


--
-- TOC entry 1227 (class 1259 OID 100539)
-- Dependencies: 1558 1559 1560 1561 5
-- Name: tytul; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE tytul (
    id_tytulu serial NOT NULL,
    data_wydania date,
    data_zakonczenia date,
    ilosc_w_serii integer,
    ilosc_posiadanych integer,
    id_rodzaju integer,
    id_zrodla integer,
    seria boolean DEFAULT false,
    adult boolean DEFAULT false,
    aktywny boolean DEFAULT true,
    data_dodania timestamp without time zone DEFAULT now()
);


--
-- TOC entry 1562 (class 1259 OID 114918)
-- Dependencies: 1219
-- Name: nazwa_tytulu_tytul_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX nazwa_tytulu_tytul_idx ON nazwa_tytulu USING btree (id_tytulu);


--
-- TOC entry 1563 (class 1259 OID 114919)
-- Dependencies: 1221
-- Name: plik_id_tytulu_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX plik_id_tytulu_idx ON plik USING btree (id_tytulu);


--
-- TOC entry 1564 (class 1259 OID 114920)
-- Dependencies: 1227
-- Name: tytul_akt_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX tytul_akt_idx ON tytul USING btree (aktywny);


--
-- TOC entry 1568 (class 0 OID 0)
-- Dependencies: 5
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- TOC entry 1569 (class 0 OID 0)
-- Dependencies: 1210
-- Name: dub; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE dub FROM PUBLIC;
REVOKE ALL ON TABLE dub FROM postgres;
GRANT ALL ON TABLE dub TO postgres;
GRANT INSERT,SELECT,UPDATE ON TABLE dub TO movie;


--
-- TOC entry 1570 (class 0 OID 0)
-- Dependencies: 1212
-- Name: genre; Type: ACL; Schema: public; Owner: pgsql
--

REVOKE ALL ON TABLE genre FROM PUBLIC;
REVOKE ALL ON TABLE genre FROM pgsql;
GRANT ALL ON TABLE genre TO pgsql;
GRANT SELECT ON TABLE genre TO movie;


--
-- TOC entry 1571 (class 0 OID 0)
-- Dependencies: 1213
-- Name: genre_tytul; Type: ACL; Schema: public; Owner: pgsql
--

REVOKE ALL ON TABLE genre_tytul FROM PUBLIC;
REVOKE ALL ON TABLE genre_tytul FROM pgsql;
GRANT ALL ON TABLE genre_tytul TO pgsql;
GRANT INSERT,SELECT,UPDATE,DELETE ON TABLE genre_tytul TO movie;


--
-- TOC entry 1572 (class 0 OID 0)
-- Dependencies: 1215
-- Name: grupa; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE grupa FROM PUBLIC;
REVOKE ALL ON TABLE grupa FROM postgres;
GRANT ALL ON TABLE grupa TO postgres;
GRANT SELECT ON TABLE grupa TO movie;


--
-- TOC entry 1573 (class 0 OID 0)
-- Dependencies: 1216
-- Name: grupa_plik; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE grupa_plik FROM PUBLIC;
REVOKE ALL ON TABLE grupa_plik FROM postgres;
GRANT ALL ON TABLE grupa_plik TO postgres;
GRANT SELECT ON TABLE grupa_plik TO movie;


--
-- TOC entry 1574 (class 0 OID 0)
-- Dependencies: 1218
-- Name: lang; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE lang FROM PUBLIC;
REVOKE ALL ON TABLE lang FROM postgres;
GRANT ALL ON TABLE lang TO postgres;
GRANT SELECT ON TABLE lang TO movie;


--
-- TOC entry 1575 (class 0 OID 0)
-- Dependencies: 1219
-- Name: nazwa_tytulu; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE nazwa_tytulu FROM PUBLIC;
REVOKE ALL ON TABLE nazwa_tytulu FROM postgres;
GRANT ALL ON TABLE nazwa_tytulu TO postgres;
GRANT INSERT,SELECT,UPDATE,DELETE ON TABLE nazwa_tytulu TO movie;


--
-- TOC entry 1576 (class 0 OID 0)
-- Dependencies: 1221
-- Name: plik; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE plik FROM PUBLIC;
REVOKE ALL ON TABLE plik FROM postgres;
GRANT ALL ON TABLE plik TO postgres;
GRANT INSERT,SELECT,UPDATE ON TABLE plik TO movie;


--
-- TOC entry 1577 (class 0 OID 0)
-- Dependencies: 1220
-- Name: plik_id_pliku_seq; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE plik_id_pliku_seq FROM PUBLIC;
REVOKE ALL ON TABLE plik_id_pliku_seq FROM postgres;
GRANT ALL ON TABLE plik_id_pliku_seq TO postgres;
GRANT UPDATE ON TABLE plik_id_pliku_seq TO movie;


--
-- TOC entry 1578 (class 0 OID 0)
-- Dependencies: 1222
-- Name: plyta; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE plyta FROM PUBLIC;
REVOKE ALL ON TABLE plyta FROM postgres;
GRANT ALL ON TABLE plyta TO postgres;
GRANT INSERT,SELECT,UPDATE,DELETE ON TABLE plyta TO movie;


--
-- TOC entry 1579 (class 0 OID 0)
-- Dependencies: 1224
-- Name: rodzaj; Type: ACL; Schema: public; Owner: pgsql
--

REVOKE ALL ON TABLE rodzaj FROM PUBLIC;
REVOKE ALL ON TABLE rodzaj FROM pgsql;
GRANT ALL ON TABLE rodzaj TO pgsql;
GRANT SELECT ON TABLE rodzaj TO movie;


--
-- TOC entry 1580 (class 0 OID 0)
-- Dependencies: 1225
-- Name: sub; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE sub FROM PUBLIC;
REVOKE ALL ON TABLE sub FROM postgres;
GRANT ALL ON TABLE sub TO postgres;
GRANT INSERT,SELECT,UPDATE ON TABLE sub TO movie;


--
-- TOC entry 1581 (class 0 OID 0)
-- Dependencies: 1227
-- Name: tytul; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE tytul FROM PUBLIC;
REVOKE ALL ON TABLE tytul FROM postgres;
GRANT ALL ON TABLE tytul TO postgres;
GRANT INSERT,SELECT,UPDATE ON TABLE tytul TO movie;


--
-- TOC entry 1582 (class 0 OID 0)
-- Dependencies: 1226
-- Name: tytul_id_tytulu_seq; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE tytul_id_tytulu_seq FROM PUBLIC;
REVOKE ALL ON TABLE tytul_id_tytulu_seq FROM postgres;
GRANT ALL ON TABLE tytul_id_tytulu_seq TO postgres;
GRANT UPDATE ON TABLE tytul_id_tytulu_seq TO movie;


-- Completed on 2006-08-09 10:58:37 CEST

--
-- PostgreSQL database dump complete
--

