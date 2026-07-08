-- Neovim configuration (symlinked to ~/.config/nvim/init.lua).
-- Deliberately minimal: nvim is the quick-edit fallback here, not the primary
-- editor (see ADR-0011). Grow this only when a need is felt in practice.

vim.opt.number = true
vim.opt.expandtab = true
vim.opt.shiftwidth = 4
vim.opt.tabstop = 4
vim.opt.smartindent = true
vim.opt.ignorecase = true
vim.opt.smartcase = true
vim.opt.undofile = true
vim.opt.clipboard = "unnamedplus"
vim.opt.termguicolors = true
