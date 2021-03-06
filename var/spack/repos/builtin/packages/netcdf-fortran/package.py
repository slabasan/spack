# Copyright 2013-2019 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *


class NetcdfFortran(AutotoolsPackage):
    """Fortran interface for NetCDF4"""

    homepage = "http://www.unidata.ucar.edu/software/netcdf"
    url      = "http://www.unidata.ucar.edu/downloads/netcdf/ftp/netcdf-fortran-4.4.3.tar.gz"

    version('4.4.5', sha256='2467536ce29daea348c736476aa8e684c075d2f6cab12f3361885cb6905717b8')
    version('4.4.4', sha256='b2d395175f8d283e68c8be516e231a96b191ade67ad0caafaf7fa01b1e6b5d75')
    version('4.4.3', sha256='330373aa163d5931e475b5e83da5c1ad041e855185f24e6a8b85d73b48d6cda9')

    variant('pic', default=True,
            description='Produce position-independent code (for shared libs)')

    depends_on('netcdf')

    # The default libtool.m4 is too old to handle NAG compiler properly:
    # https://github.com/Unidata/netcdf-fortran/issues/94
    patch('nag.patch', when='@:4.4.4%nag')

    def flag_handler(self, name, flags):
        if name in ['cflags', 'fflags'] and '+pic' in self.spec:
            flags.append(self.compiler.pic_flag)
        elif name == 'cppflags':
            flags.append(self.spec['netcdf'].headers.cpp_flags)
        elif name == 'ldflags':
            # We need to specify LDFLAGS to get correct dependency_libs
            # in libnetcdff.la, so packages that use libtool for linking
            # could correctly link to all the dependencies even when the
            # building takes place outside of Spack environment, i.e.
            # without Spack's compiler wrappers.
            flags.append(self.spec['netcdf'].libs.search_flags)

        return None, None, flags

    @property
    def libs(self):
        libraries = ['libnetcdff']

        # This package installs both shared and static libraries. Permit
        # clients to query which one they want.
        query_parameters = self.spec.last_query.extra_parameters
        shared = 'shared' in query_parameters

        return find_libraries(
            libraries, root=self.prefix, shared=shared, recursive=True
        )
