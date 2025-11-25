#include "serializer.h"
#include "external/cJSON.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>


cJSON *SerializeObject(void *data, StructScheme *scheme)
{
	cJSON *json = cJSON_CreateObject();

	for (int i = 0; i < scheme->fieldCount; i++)
	{
		void *address = (char *) data + scheme->fields[i].offset;

		switch (scheme->fields[i].type)
		{
			case INT:
			case ENUM:
				cJSON_AddNumberToObject(json, scheme->fields[i].name, *(int *) address);
				break;

			case FLOAT:
				cJSON_AddNumberToObject(json, scheme->fields[i].name, *(float *) address);
				break;

			case STRING:
				cJSON_AddStringToObject(json, scheme->fields[i].name, *(char **) address);
				break;

			case STRUCT:
				if (*(void **) address != NULL)
				{
					cJSON *childObject = SerializeObject(*(void **) address, scheme->fields[i].childScheme);
					cJSON_AddItemToObject(json, scheme->fields[i].name, childObject);
				}
				else
				{
					cJSON_AddNullToObject(json, scheme->fields[i].name);
				}
				break;

			case BOOL:
				cJSON_AddBoolToObject(json, scheme->fields[i].name, *(bool *) address);
				break;

			case LONG:
				cJSON_AddNumberToObject(json, scheme->fields[i].name, (double) *(long *) address);
				break;

			case DOUBLE:
				cJSON_AddNumberToObject(json, scheme->fields[i].name, *(double *) address);
				break;

			default:
				printf("Unknown type for field: %s\n", scheme->fields[i].name);
				break;
		}
	}

	return json;
}


void *DeserializeObject(cJSON *jsonObject, StructScheme *scheme)
{
	void *object = calloc(1, scheme->size);

	for (int i = 0; i < scheme->fieldCount; i++)
	{
		void *address = (char *) object + scheme->fields[i].offset;
		cJSON *item = cJSON_GetObjectItemCaseSensitive(jsonObject, scheme->fields[i].name);

		if (!item)
		{
			continue;
		}

		switch (scheme->fields[i].type)
		{
			case INT:
			case ENUM:
			{
				*(int *) address = item->valueint;
				break;
			}

			case FLOAT:
			{
				*(float *) address = (float) item->valuedouble;
				break;
			}

			case STRING:
			{
				if (cJSON_IsString(item) && item->valuestring != NULL)
				{
					char *copy = malloc(strlen(item->valuestring) + 1);
					strcpy(copy, item->valuestring);
					*(char **) address = copy;
				}
				else
				{
					*(char **) address = NULL;
				}
				break;
			}

			case STRUCT:
			{
				void *childObject = DeserializeObject(item, scheme->fields[i].childScheme);
				*(void **) address = childObject;
				break;
			}

			case BOOL:
			{
				*(bool *) address = cJSON_IsTrue(item);
				break;
			}

			case LONG:
			{
				*(long *) address = (long) item->valuedouble;
				break;
			}

			case DOUBLE:
			{
				*(double *) address = item->valuedouble;
				break;
			}
		}
	}

	return object;
}


char *SerializeToJson(void *data, StructScheme *scheme)
{
	cJSON *json = SerializeObject(data, scheme);
	char *jsonString = cJSON_Print(json);
	cJSON_Delete(json);
	return jsonString;
}


void *DeserializeFromJson(char *jsonString, StructScheme *scheme)
{
	cJSON *jsonObject = cJSON_Parse(jsonString);
	if (!jsonObject)
	{
		return NULL;
	}
	void *object = DeserializeObject(jsonObject, scheme);
	cJSON_Delete(jsonObject);
	return object;
}
