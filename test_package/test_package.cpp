#include <iostream>
#include <CEGUI/RendererModules/Null/Renderer.h>

int main()
{
	const CEGUI::NullRenderer & renderer = CEGUI::NullRenderer::bootstrapSystem();
    return 0;
}
