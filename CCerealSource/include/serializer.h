#pragma once
#define SERIALIZABLE
#include <stddef.h>

typedef enum
{
	INT,
	FLOAT,
	STRING,
	STRUCT,
	BOOL,
	LONG,
	DOUBLE,
	ENUM
} FieldType;

typedef struct
{
	char *name;
	int offset;
	FieldType type;
	struct StructScheme *childScheme;
} FieldInfo;

typedef struct StructScheme
{
	char *name;
	int fieldCount;
	FieldInfo *fields;
	size_t size;
} StructScheme;


char *SerializeToJson(void *data, StructScheme *scheme);

void *DeserializeFromJson(char *jsonString, StructScheme *scheme);
