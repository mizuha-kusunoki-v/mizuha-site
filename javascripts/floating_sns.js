document.addEventListener('DOMContentLoaded', function () {
  const container = document.createElement('div');
  container.className = 'sns-float';
  container.innerHTML = `
    <a class="sns-float-btn sns-youtube"
       href="https://www.youtube.com/@楠木瑞羽"
       target="_blank" rel="noopener" aria-label="YouTube">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
        <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12
          3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0
          12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505
          9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24
          12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
      </svg>
      <span class="sns-float-label">YouTube</span>
    </a>
    <a class="sns-float-btn sns-x"
       href="https://x.com/Mizuha_live"
       target="_blank" rel="noopener" aria-label="X 配信告知">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
        <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401
          6.231H2.744l7.737-8.835L1.254 2.25H8.08l4.253 5.622 5.912-5.622zm-1.161
          17.52h1.833L7.084 4.126H5.117z"/>
      </svg>
      <span class="sns-float-label">配信告知</span>
    </a>
  `;
  document.body.appendChild(container);
});
