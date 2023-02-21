import json
import pathlib

import click
from click import echo

from ..decorators import (
    bunch_size_option,
    end_date_option,
    pass_client,
    pass_session,
    start_date_option,
    timeout_option,
)
from ..models import Library
from ..utils import export_to_csv


@click.group("library")
def cli():
    """Interact with library."""


async def _get_library(session, client, resolve_podcasts):
    bunch_size = session.params.get("bunch_size")
    start_date = session.params.get("start_date")
    end_date = session.params.get("end_date")

    library = await Library.from_api_full_sync(
        client,
        response_groups=(
            "contributors, media, price, product_attrs, product_desc, "
            "product_extended_attrs, product_plan_details, product_plans, "
            "rating, sample, sku, series, reviews, ws4v, origin, "
            "relationships, review_attrs, categories, badge_types, "
            "category_ladders, claim_code_url, is_downloaded, "
            "is_finished, is_returnable, origin_asin, pdf_url, "
            "percent_complete, provided_review"
        ),
        bunch_size=bunch_size,
        start_date=start_date,
        end_date=end_date,
    )

    if resolve_podcasts:
        await library.resolve_podcasts(start_date=start_date, end_date=end_date)

    return library


@cli.command("export")
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=pathlib.Path),
    default=pathlib.Path().cwd() / r"library.{format}",
    show_default=True,
    help="output file",
)
@timeout_option
@click.option(
    "--format",
    "-f",
    type=click.Choice(["tsv", "csv", "json"]),
    default="tsv",
    show_default=True,
    help="Output format",
)
@bunch_size_option
@click.option(
    "--resolve-podcasts", is_flag=True, help="Resolve podcasts to show all episodes"
)
@start_date_option
@end_date_option
@pass_session
@pass_client
async def export_library(session, client, **params):
    """Export library."""

    def _prepare_item(item):
        keys_with_raw_values = (
            "asin",
            "title",
            "subtitle",
            "extended_product_description",
            "runtime_length_min",
            "is_finished",
            "percent_complete",
            "release_date",
            "purchase_date",
        )
        data_row = {}
        for key in item:
            value = getattr(item, key)
            if value is None:
                continue

            if key in keys_with_raw_values:
                data_row[key] = value
            elif key in ("authors", "narrators"):
                data_row[key] = ", ".join([i["name"] for i in value])
            elif key == "series":
                data_row["series_title"] = value[0]["title"]
                data_row["series_sequence"] = value[0]["sequence"]
            elif key == "rating":
                overall_distributing = value.get("overall_distribution") or {}
                data_row["rating"] = overall_distributing.get(
                    "display_average_rating", "-"
                )
                data_row["num_ratings"] = overall_distributing.get("num_ratings", "-")
            elif key == "library_status":
                data_row["date_added"] = value["date_added"]
            elif key == "product_images":
                data_row["cover_url"] = value.get("500", "-")
            elif key == "category_ladders":
                genres = []
                for genre in value:
                    for ladder in genre["ladder"]:
                        genres.append(ladder["name"])
                data_row["genres"] = ", ".join(genres)

        return data_row

    output_format = params.get("format")
    output_filename: pathlib.Path = params.get("output")
    if output_filename.suffix == r".{format}":
        suffix = "." + output_format
        output_filename = output_filename.with_suffix(suffix)

    resolve_podcasts = params.get("resolve_podcasts")
    library = await _get_library(session, client, resolve_podcasts)
    prepared_library = list(
        filter(lambda x: x is not None, map(_prepare_item, library))
    )
    prepared_library.sort(key=lambda x: x["asin"])

    if output_format in ("tsv", "csv"):
        headers = (
            "asin",
            "title",
            "subtitle",
            "extended_product_description",
            "authors",
            "narrators",
            "series_title",
            "series_sequence",
            "genres",
            "runtime_length_min",
            "is_finished",
            "percent_complete",
            "rating",
            "num_ratings",
            "date_added",
            "release_date",
            "cover_url",
            "purchase_date",
        )
        dialect = "excel" if output_format == "csv" else "excel-tab"
        export_to_csv(output_filename, prepared_library, headers, dialect)

    else:
        data = json.dumps(prepared_library, indent=4)
        output_filename.write_text(data)


@cli.command("list")
@timeout_option
@bunch_size_option
@click.option(
    "--resolve-podcasts", is_flag=True, help="Resolve podcasts to show all episodes"
)
@start_date_option
@end_date_option
@pass_session
@pass_client
async def list_library(session, client, resolve_podcasts):
    """List library."""

    def _prepare_item(item):
        fields = [item.asin]

        if item.authors:
            fields.append(", ".join(sorted(a["name"] for a in item.authors)))

        if item.series:
            fields.append(", ".join(sorted(s["title"] for s in item.series)))

        fields.append(item.title)
        return ": ".join(fields)

    library = await _get_library(session, client, resolve_podcasts)
    books = sorted(map(_prepare_item, library))
    list(map(echo, filter(lambda x: len(x) > 0, books)))
