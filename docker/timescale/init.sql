CREATE TABLE curso(
	id TEXT NOT NULL,
	name TEXT NOT NULL,
	profesor TEXT NOT NULL,
	created_at TIMESTAMPTZ NOT NULL,

	PRIMARY KEY (id)
);


CREATE OR REPLACE FUNCTION insert_curso(_id TEXT,_name TEXT, _profesor TEXT, _created_at TIMESTAMP WITH TIME ZONE) RETURNS VOID
	LANGUAGE plpgsql
	AS $$
BEGIN
	INSERT INTO curso(
		id,
		name,
		profesor,
		created_at
	)
	values (
		_id,
		_name,
		_profesor,
		_created_at
	);
END;
$$;


CREATE OR REPLACE FUNCTION deleted_curso(_id TEXT) RETURNS VOID
    LANGUAGE plpgsql
    AS $$
BEGIN
    DELETE FROM curso  WHERE id = _id;
END;
$$;

CREATE OR REPLACE FUNCTION select_cursos()
	RETURNS TABLE(name TEXT, profesor TEXT)
	LANGUAGE plpgsql
	AS $$
BEGIN
	RETURN QUERY SELECT c.name, c.profesor FROM curso c  ORDER BY c.created_at DESC;
END;
$$;


