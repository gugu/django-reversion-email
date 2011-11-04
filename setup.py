from distutils.core import setup


# Load in babel support, if available.
try:
    from babel.messages import frontend as babel
    cmdclass = {"compile_catalog": babel.compile_catalog,
                "extract_messages": babel.extract_messages,
                "init_catalog": babel.init_catalog,
                "update_catalog": babel.update_catalog,}
except ImportError:
    cmdclass = {}


setup(name="django-reversion-email",
      version="0.1",
      description="An extension to django-reversion, which sends notifications about changing models",
      author="Andrii Kostenko",
      author_email="andrey@kostenko.name",
      url="http://github.com/gugu/django-reversion-email",
      download_url="http://github.com/downloads/gugu/django-reversion-email/django-reversion-email-0.1.tar.gz",
      zip_safe=False,
      packages=["reversion_email"],
      package_dir={"": "src"},
      package_data = {"reversion_email": ["templates/reversion_email/*.*"]},
      cmdclass = cmdclass,
      classifiers=["Development Status :: 5 - Production/Stable",
                   "Environment :: Web Environment",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: BSD License",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python",
                   "Framework :: Django",])
