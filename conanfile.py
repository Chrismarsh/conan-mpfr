import os, shutil, platform
from conans import ConanFile, AutoToolsBuildEnvironment, tools

class MpfrConan(ConanFile):
    """ Building MPFR for the intention of using it to build CGAL """

    name        = 'mpfr'
    description = 'The GNU Multiple Precision Arithmetic Library'
    url         = 'https://github.com/Chrismarsh/conan-mpfr'
    license     = 'MIT'
    settings    = 'os', 'compiler', 'arch', 'build_type'
    requires    = 'gmp/[>=5.0.0]@CHM/stable'

    # See http://www.mpfr.org/mpfr-current/mpfr.pdf for other potential options
    options = {
        'shared':            [True, False],
        'static':            [True, False]
    }
    default_options = 'shared=True', 'static=True'

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
       
        shutil.move('mpfr-{version}'.format(version=self.version), self.name)
        tools.replace_in_file(self.name+"/configure", r"-install_name \$rpath/", "-install_name @rpath/")

    def build(self):
        with tools.chdir(self.name):
            autotools = AutoToolsBuildEnvironment(self, win_bash=(platform.system() == "Windows"))

            env_vars = {}
            args = []

            args.append('--prefix=%s'%self.package_folder)

            args.append('--%s-shared'%('enable' if self.options.shared else 'disable'))
            args.append('--%s-static'%('enable' if self.options.static else 'disable'))


            autotools.fpic = True
            if self.settings.arch == 'x86':
                env_vars['ABI'] = '32'
                autotools.cxx_flags.append('-m32')

            # Add GMP
            autotools.library_paths.append(os.path.join(self.deps_cpp_info['gmp'].rootpath, self.deps_cpp_info['gmp'].libdirs[0]))
            autotools.include_paths.append(os.path.join(self.deps_cpp_info['gmp'].rootpath, self.deps_cpp_info['gmp'].includedirs[0]))

            # Debug
            self.output.info('Configure arguments: %s'%' '.join(args))

            # Set up our build environment
            with tools.environment_append(env_vars):
                autotools.configure(args=args)

            autotools.make()
            autotools.make(args=['install'])

    def package(self):
        self.copy("COPYING*", src="mpfr", dst="")
        self.copy("mpfr.lib",  src="mpfr", dst="lib")

    def package_info(self):
        self.cpp_info.libs = ['mpfr']

