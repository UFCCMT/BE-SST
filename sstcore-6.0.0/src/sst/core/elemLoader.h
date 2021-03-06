// Copyright 2009-2016 Sandia Corporation. Under the terms
// of Contract DE-AC04-94AL85000 with Sandia Corporation, the U.S.
// Government retains certain rights in this software.
//
// Copyright (c) 2009-2016, Sandia Corporation
// All rights reserved.
//
// This file is part of the SST software package. For license
// information, see the LICENSE file in the top level directory of the
// distribution.

#ifndef _SST_CORE_ELEMLOADER_H
#define _SST_CORE_ELEMLOADER_H

#include <string>
#include <sst/core/element.h>

namespace SST {

struct LoaderData;

/** Class to load Element Libraries */
class ElemLoader {
    LoaderData *loaderData;
    std::string searchPaths;
public:
    /** Create a new ElementLoader with a given searchpath of directories */
    ElemLoader(const std::string &searchPaths);
    ~ElemLoader();

    /** Attempt to load a library
     * @param elemlib - The name of the Element Library to load
     * @param showErrors - Print errors associated with attempting to find and load the library
     * @return Informational structure of the library, or NULL if it failed to load.
     */
    const ElementLibraryInfo* loadLibrary(const std::string &elemlib, bool showErrors);
};

}

#endif /* _SST_CORE_ELEMLOADER_H */
