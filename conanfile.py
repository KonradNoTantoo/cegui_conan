from conans import ConanFile, CMake, tools
import os


class CeguiConan(ConanFile):
    name = "cegui"
    version = "0.8.190523"
    license = "MIT"
    author = "konrad"
    url = "https://github.com/KonradNoTantoo/cegui_conan"
    description = "Crazy Eddie's GUI is a user interface library with a number of supported backends"
    topics = ("Graphic UI", "graphics", "game UI", "games", "conan")
    settings = "os", "compiler", "build_type", "arch"
    # TODO handle static builds
    # TODO handle python scripting (needs boost_python lib)
    # TODO handle extra renderers, image loaders and XML parsers
    options = {
        "lua_scripting": [True, False],
        "ogre_renderer": [True, False],
        "direct3d9_renderer": [True, False],
        "direct3d10_renderer": [True, False],
        "direct3d11_renderer": [True, False],
        "opengl_renderer": [True, False],
        "opengl3_renderer": [True, False],
        "opengles_renderer": [True, False],
    }
    default_options = {
        "lua_scripting": True,
        "ogre_renderer": True,
        "direct3d9_renderer": False,
        "direct3d10_renderer": False,
        "direct3d11_renderer": False,
        "opengl_renderer": False,
        "opengl3_renderer": False,
        "opengles_renderer": False,
    }
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

    scm = {
        "type": "git",
        "subfolder": folder_name,
        "url": "https://github.com/cegui/cegui.git",
        # 2019.05.23 commit on v0-8 branch
        "revision": "be649b6d582e7f5c613526e33f0bab871c02a4b6",
        "submodule": "recursive" 
    }


    def configure(self):
        if self.settings.os == "Linux":
            self.options.direct3d9_renderer = False
            self.options.direct3d10_renderer = False
            self.options.direct3d11_renderer = False


    def requirements(self):
        if self.options.lua_scripting:
            self.requires("toluapp/1.0.93@utopia/testing")
        if self.options.ogre_renderer:
            self.requires("ogre3d/1.12.5@utopia/testing")


    def source(self):
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
        cmake.definitions["CEGUI_SAMPLES_ENABLED"] = "OFF"
 
        cmake.definitions["CEGUI_BUILD_RENDERER_NULL"] = "ON"
        cmake.definitions["CEGUI_BUILD_RENDERER_OGRE"] = "ON" if self.options.ogre_renderer else "OFF"
        cmake.definitions["CEGUI_BUILD_RENDERER_DIRECT3D9"] = "ON" if self.options.direct3d9_renderer else "OFF"
        cmake.definitions["CEGUI_BUILD_RENDERER_DIRECT3D10"] = "ON" if self.options.direct3d10_renderer else "OFF"
        cmake.definitions["CEGUI_BUILD_RENDERER_DIRECT3D11"] = "ON" if self.options.direct3d11_renderer else "OFF"
        cmake.definitions["CEGUI_BUILD_RENDERER_OPENGL"] = "ON" if self.options.opengl_renderer else "OFF"
        cmake.definitions["CEGUI_BUILD_RENDERER_OPENGL3"] = "ON" if self.options.opengl3_renderer else "OFF"
        cmake.definitions["CEGUI_BUILD_RENDERER_OPENGLES"] = "ON" if self.options.opengles_renderer else "OFF"

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
            "CEGUILuaScriptModule-0",
            "CEGUINullRenderer-0",
        ]

        if self.options.ogre_renderer:
            libs.append("CEGUIOgreRenderer-0")
        if self.options.direct3d9_renderer:
            libs.append("CEGUIDirect3D9Renderer-0")
        if self.options.direct3d10_renderer:
            libs.append("CEGUIDirect3D10Renderer-0")
        if self.options.direct3d11_renderer:
            libs.append("CEGUIDirect3D11Renderer-0")
        if self.options.opengl_renderer:
            libs.append("CEGUIOpenGLRenderer-0")
        if self.options.opengl3_renderer:
            libs.append("CEGUIOpenGL3Renderer-0")
        if self.options.opengles_renderer:
            libs.append("CEGUIOpenGLESRenderer-0")

        if self.settings.compiler == "Visual Studio" and self.settings.build_type == "Debug":
            self.cpp_info.libs = [lib + "_d" for lib in libs]
        else:
            self.cpp_info.libs = libs

        self.cpp_info.includedirs = [os.path.join("include", "cegui-0")]

