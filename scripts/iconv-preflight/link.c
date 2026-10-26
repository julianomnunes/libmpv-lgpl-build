#include <iconv.h>
int main(void)
{
    iconv_t converter = iconv_open("UTF-8", "UTF-8");
    if (converter == (iconv_t)-1)
        return 1;
    return iconv_close(converter);
}
