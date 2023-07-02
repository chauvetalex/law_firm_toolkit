.DEFAULT_GOAL= help

say_hello: ## Exemple
	@python -c 'print("hello $(NAME)");'{}

split_pdf: ## Retourne le nombre de cerfas pouvant être envoyés.
	@python -c 'from law_firm_toolkit.office_suites_utils.pdf_utils import split_pdf_tui; print("$(PDF_FILE)"); split_pdf_tui("$(PDF_FILE)")'

del_pages_pdf:
	@python -c 'from law_firm_toolkit.office_suites_utils.pdf_utils import delete_pages; delete_pages(src_pdf_file="$(src_file)", dst_pdf_file="$(dst_file)", pages=$(del_pages))'

folder='raw_data/test_utils/stamper'
stamp='raw_data/test_utils/stamper/tampon_boissy.png'
resize_ratio='0.65'
stamped_pages='[1]'
stamp_pdf:
	@python -c 'from law_firm_toolkit import stamper; stamper.documents_lawyer_stamper(docs_folder="$(folder)", stamp="$(stamp)", resize=$(resize_ratio), stamped_pages=$(stamped_pages))'

quote:
	@python law_firm_toolkit/quote_maker.py

help:
	@grep -E '(^[a-zA-Z_-]+:.*?##.*$$)|(^##)' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[32m%-10s\033[0m %s\n", $$1, $$2}' | sed -e 's/\[32m##/[33m/'
