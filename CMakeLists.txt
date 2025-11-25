cmake_minimum_required(VERSION 4.0)

project(CCereal C)


add_library(CCereal STATIC
        CCerealSource/src/serializer.c
        CCerealSource/src/external/cJSON.c
)


target_include_directories(CCereal
        PUBLIC
        CCerealSource/include
        CCerealSource/meta_data
        PRIVATE
        CCerealSource/src/external
)


install(TARGETS CCereal
        ARCHIVE DESTINATION lib
        LIBRARY DESTINATION lib
        RUNTIME DESTINATION bin
)

install(FILES CCerealSource/include/serializer.h
        DESTINATION include)

install(FILES CCerealSource/tools/meta_generator.py
        DESTINATION tools)

install(FILES CCerealSource/bin/gen_meta.bat
        DESTINATION bin)