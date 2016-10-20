import numpy
setup(
  name ='time stamp binner',
  cmdclass = {'build_ext': build_ext},
  ext_modules = ext_modules,
  include_dirs = [numpy.get_include()] #Include directory not hard-wired
)
