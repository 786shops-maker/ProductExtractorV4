"""
exceptions.py - Custom exceptions for ProductExtractorV3
"""

class ProductExtractorError(Exception):
    """Base exception for all ProductExtractor errors."""
    pass


class ConfigurationError(ProductExtractorError):
    """Configuration is invalid or missing."""
    pass


class FetchError(ProductExtractorError):
    """Failed to fetch a webpage."""
    pass


class ParserError(ProductExtractorError):
    """Failed to parse HTML or product data."""
    pass


class JSONLDParserError(ParserError):
    """Failed to parse JSON-LD."""
    pass


class WebsiteDetectionError(ParserError):
    """Unable to determine supported website."""
    pass


class BrandDetectionError(ParserError):
    """Unable to determine product brand."""
    pass


class PriceParserError(ParserError):
    """Price extraction failed."""
    pass


class DescriptionParserError(ParserError):
    """Description extraction failed."""
    pass


class ImageFinderError(ProductExtractorError):
    """Image discovery failed."""
    pass


class ImageSelectionError(ProductExtractorError):
    """Image selection failed."""
    pass


class ImageDownloadError(ProductExtractorError):
    """Image download failed."""
    pass


class ImageProcessingError(ProductExtractorError):
    """Image processing failed."""
    pass


class OutputWriterError(ProductExtractorError):
    """Writing output failed."""
    pass


class ValidationError(ProductExtractorError):
    """Product validation failed."""
    pass
