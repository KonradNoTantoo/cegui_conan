from conans import ConanFile, CMake, tools
import os


class CeguiConan(ConanFile):
    name = "cegui"
    version = "0.8.7"
    license = "MIT"
    author = "konrad"
    url = "https://github.com/KonradNoTantoo/cegui_conan"
    description = "Crazy Eddie's GUI is a user interface library with a number of supported backends"
    topics = ("Graphic UI", "graphics", "game UI", "games", "conan")
    settings = "os", "compiler", "build_type", "arch"
    # TODO handle static builds
    # TODO handle python scripting (needs boost_python lib)
    # TODO handle extra renderers, image loaders and XML parsers
    options = {"lua_scripting": [True, False], "ogre_renderer": [True, False]}
    default_options = {"lua_scripting": True, "ogre_renderer": True}
    generators = "cmake"
    folder_name = "{}-{}".format(name, version)
    boost_version = "1.71.0"
    requires = [
        ("boost/{}@conan/stable".format(boost_version)),
        ("xerces-c/3.2.2@bincrafters/stable"),
        ("libpng/1.6.37@bincrafters/stable", "override"),
        ("freetype/2.10.0@bincrafters/stable"),
        ("freeimage/3.18.0@utopia/testing"),
    ]


    def requirements(self):
        if self.options.lua_scripting:
            self.requires("toluapp/1.0.93@utopia/testing")
        if self.options.ogre_renderer:
            self.requires("ogre/1.12.5@utopia/testing")


    def source(self):
        tarball_path = "http://prdownloads.sourceforge.net/crayzedsgui/{}.tar.bz2".format(self.folder_name)
        tools.get(tarball_path)
        tools.replace_in_file("{}/CMakeLists.txt".format(self.folder_name), "project(cegui)",
                              '''project(cegui)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()
link_libraries(${CONAN_LIBS})''')

        # following line doesn't suffice for cmake to find wanted boost static libs
        # tools.replace_in_file("{}/CMakeLists.txt".format(self.folder_name), "find_package(Boost 1.36.0 COMPONENTS python unit_test_framework system timer)",
                            # "find_package(Boost {})".format(self.boost_version))


    def configure_cmake(self):
        cmake = CMake(self)

        cmake.definitions["CEGUI_BUILD_APPLICATION_TEMPLATES"] = "OFF"
        cmake.definitions["CEGUI_BUILD_LUA_MODULE"] = "ON" if self.options.lua_scripting else "OFF"
        cmake.definitions["CEGUI_BUILD_RENDERER_OGRE"] = "ON" if self.options.ogre_renderer else "OFF"
        cmake.definitions["CEGUI_SAMPLES_ENABLED"] = "OFF"

        cmake.configure(source_folder=self.folder_name)
        return cmake

    def build(self):
        cmake = self.configure_cmake()
        cmake.build()

    def package(self):
        cmake = self.configure_cmake()
        cmake.install()

    def package_info(self):
        libs = [
            "CEGUIBase-0",
            "CEGUICommonDialogs-0",
            "CEGUICoreWindowRendererSet",
            "CEGUIDirect3D9Renderer-0",
            "CEGUIDirect3D10Renderer-0",
            "CEGUIFreeImageImageCodec",
            "CEGUILuaScriptModule-0",
            "CEGUIOgreRenderer-0",
            "CEGUIXercesParser",
        ]
        self.cpp_info.libs = [lib + "_d" if self.settings.build_type == "Debug" else lib for lib in libs]
        self.cpp_info.includedirs = [os.path.join("include", "cegui-0")]

