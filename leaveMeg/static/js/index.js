new fullpage('#fullpage', {
            autoScrolling: true,
            scrollHorizontally: true,
            navigation:false,
       verticalCentered: false,
            afterLoad: function(origin, destination, direction) {
                // 如果是最后一页，隐藏所有箭头
                if (destination.index === 2) {
                    document.querySelectorAll('.down-arrow').forEach(arrow => {
                        arrow.style.display = 'none';
                    });
                } else {
                    document.querySelectorAll('.down-arrow').forEach(arrow => {
                        arrow.style.display = 'block';
                    });
                }
            }
        });
        var typed = new Typed('#element', {
            strings: [
                " 听，谐乐的低吟更加清晰了……",
                " 万事俱备，到了登台演出的时刻了。",
                " 乐曲之外的准备也不能懈怠。",
                "偶尔戴上假发，换个妆容，再戴一副眼镜——这样去哪都不用担心了~",
                "梦醒之后，我们都将面对现实。我们…哥哥的梦想，也将从此开始。",
            ],
            typeSpeed: 80,
            backSpeed: 50,
            loop: true,
        });

        // 可选：添加随机气泡大小和位置（增强动态感）
        document.addEventListener('DOMContentLoaded', function() {
            const bubbles = document.querySelectorAll('.bubble');
            bubbles.forEach(bubble => {
                // 随机调整大小（±10%）
                const sizeRatio = 0.9 + Math.random() * 0.2;
                bubble.style.width = `${parseInt(bubble.style.width) * sizeRatio}px`;
                bubble.style.height = `${parseInt(bubble.style.height) * sizeRatio}px`;

                // 随机调整初始透明度
                bubble.style.opacity = 0.5 + Math.random() * 0.4;
            });
        });