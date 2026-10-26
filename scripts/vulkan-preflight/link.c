#include <vulkan/vulkan.h>
#include <stdio.h>
_Static_assert(VK_HEADER_VERSION == 345, "Require exact locked headers");
int main(void) {
    uint32_t version = 0;
    VkResult result = vkEnumerateInstanceVersion(&version);
    printf("loader_result=%d api_version=%u\n", result, version);
    return result != VK_SUCCESS || version < VK_MAKE_API_VERSION(0, 1, 4, 345);
}
