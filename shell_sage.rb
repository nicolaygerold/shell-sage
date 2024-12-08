class ShellSage < Formula
    include Language::Python::Virtualenv

    desc "AI-powered shell commands in your terminal"
    homepage "https://github.com/nicolaygerold/homebrew-shell-sage"
    url "https://github.com/nicolaygerold/homebrew-shell-sage/archive/refs/tags/v0.0.1.tar.gz"
    sha256 "d5558cd419c8d46bdc958064cb97f963d1ea793866414c025906ec15033512ed"
    license "Apache-2.0"

    depends_on "python@3.12"

    resource "aisuite" do
      url "https://files.pythonhosted.org/packages/source/a/aisuite/aisuite-0.1.6.tar.gz"
      sha256 "0937372a4aa369ad63fa2350cf58780fdad6914e651e97ca7f6192a517e933b7"
    end

    resource "anthropic" do
      url "https://files.pythonhosted.org/packages/source/a/anthropic/anthropic-0.40.0.tar.gz"
      sha256 "3efeca6d9e97813f93ed34322c6c7ea2279bf0824cd0aa71b59ce222665e2b87"
    end

    resource "openai" do
      url "https://files.pythonhosted.org/packages/source/o/openai/openai-1.57.0.tar.gz"
      sha256 "76f91971c4bdbd78380c9970581075e0337b5d497c2fbf7b5255078f4b31abf9"
    end

    resource "rich" do
      url "https://files.pythonhosted.org/packages/source/r/rich/rich-13.9.4.tar.gz"
      sha256 "439594978a49a09530cff7ebc4b5c7103ef57baf48d5ea3184f21d9a2befa098"
    end

    resource "typer" do
      url "https://files.pythonhosted.org/packages/source/t/typer/typer-0.15.1.tar.gz"
      sha256 "a0588c0a7fa68a1978a069818657778f86abe6ff5ea6abf472f940a08bfe4f0a"
    end

    def install
      virtualenv_install_with_resources
    end

    test do
      assert_match "ShellSage", shell_output("#{bin}/ssage --help")
    end
  end